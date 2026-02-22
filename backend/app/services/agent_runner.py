import asyncio
import json
import logging
import time
from collections.abc import Callable
from pathlib import Path

import anthropic

from app.models.schemas import AgentResponse
from app.services.prompt_manager import format_agent_prompt, format_evaluation_prompt

logger = logging.getLogger(__name__)

# Sentiment keyword lists for simple MVP detection
_POSITIVE_WORDS = [
    "love", "great", "amazing", "fantastic", "excellent", "perfect",
    "definitely", "would buy", "i'd buy", "sign me up", "excited",
    "awesome", "wonderful", "brilliant", "yes", "absolutely",
    "interested", "want", "need this", "can't wait", "impressive",
]
_NEGATIVE_WORDS = [
    "don't like", "wouldn't", "not interested", "dislike", "hate",
    "terrible", "awful", "no way", "pass", "skip", "not for me",
    "waste", "disappointed", "overpriced", "cheap", "wouldn't buy",
    "don't need", "not worth", "ugly", "boring",
]


def detect_sentiment(text: str) -> str:
    """Simple keyword-based sentiment detection for visualization color coding.

    Returns 'positive', 'negative', or 'neutral'.
    """
    lower = text.lower()
    pos_count = sum(1 for w in _POSITIVE_WORDS if w in lower)
    neg_count = sum(1 for w in _NEGATIVE_WORDS if w in lower)

    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    return "neutral"


class AgentRunner:
    """Runs customer persona agents in parallel against a product description."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_concurrent: int = 50,
    ) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def run_single_agent(
        self,
        profile_id: str,
        persona_prompt: str,
        product_description: str,
        manifest_entry: dict | None = None,
    ) -> AgentResponse:
        """Run a single agent with semaphore-based rate limiting.

        Returns an AgentResponse on success, or an error response on failure.
        """
        start = time.monotonic()
        display_name = (manifest_entry or {}).get("display_name", profile_id[:12])
        age = (manifest_entry or {}).get("age", 0)
        segments = (manifest_entry or {}).get("segments", [])
        segment = segments[0] if segments else "unknown"

        try:
            async with self.semaphore:
                system_prompt = format_agent_prompt(persona_prompt)
                user_message = format_evaluation_prompt(product_description)

                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                )

                response_text = response.content[0].text
                elapsed_ms = (time.monotonic() - start) * 1000

                return AgentResponse(
                    agent_id=profile_id,
                    profile_name=display_name,
                    age=age,
                    segment=segment,
                    response_text=response_text,
                    sentiment=detect_sentiment(response_text),
                    response_time_ms=round(elapsed_ms, 1),
                )

        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Agent %s failed: %s", profile_id, e)
            return AgentResponse(
                agent_id=profile_id,
                profile_name=display_name,
                age=age,
                segment=segment,
                response_text=f"[Error: {type(e).__name__}]",
                sentiment="neutral",
                response_time_ms=round(elapsed_ms, 1),
            )

    async def run_all_agents(
        self,
        product_description: str,
        processed_dir: str = "data/processed",
        max_agents: int | None = None,
        callback: Callable | None = None,
    ) -> list[AgentResponse]:
        """Run all persona agents in parallel.

        Args:
            product_description: The product/change to evaluate.
            processed_dir: Directory with persona .txt files and manifest.json.
            max_agents: Limit number of agents (None = all).
            callback: Called with each AgentResponse as it completes (for SSE streaming).

        Returns:
            List of all AgentResponse objects.
        """
        processed_path = Path(processed_dir)
        manifest_path = processed_path / "manifest.json"

        with open(manifest_path) as f:
            manifest: dict = json.load(f)

        # Build list of (profile_id, persona_text, manifest_entry)
        agent_inputs: list[tuple[str, str, dict]] = []
        for profile_id, entry in manifest.items():
            persona_file = entry["persona_file"]
            persona_path = Path(persona_file)

            # Try multiple resolution strategies:
            # 1. Absolute or already correct relative path
            # 2. Relative to processed_dir
            # 3. Filename only, in processed_dir
            if not persona_path.exists():
                persona_path = processed_path / persona_file
            if not persona_path.exists():
                persona_path = processed_path / Path(persona_file).name

            persona_text = persona_path.read_text()
            agent_inputs.append((profile_id, persona_text, entry))

        if max_agents is not None:
            agent_inputs = agent_inputs[:max_agents]

        total = len(agent_inputs)
        logger.info(
            "Starting %d agents (model=%s, concurrency=%d)",
            total,
            self.model,
            self.semaphore._value,
        )
        start = time.monotonic()

        async def run_with_callback(
            pid: str, persona: str, entry: dict
        ) -> AgentResponse:
            result = await self.run_single_agent(
                pid, persona, product_description, entry
            )
            if callback is not None:
                await callback(result)
            return result

        tasks = [
            run_with_callback(pid, persona, entry)
            for pid, persona, entry in agent_inputs
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert any unexpected exceptions to error responses
        responses: list[AgentResponse] = []
        failures = 0
        for i, r in enumerate(results):
            if isinstance(r, AgentResponse):
                responses.append(r)
                if r.response_text.startswith("[Error:"):
                    failures += 1
            elif isinstance(r, Exception):
                failures += 1
                pid, _, entry = agent_inputs[i]
                logger.error("Unexpected exception for agent %s: %s", pid, r)
                responses.append(
                    AgentResponse(
                        agent_id=pid,
                        profile_name=entry.get("display_name", pid[:12]),
                        age=entry.get("age", 0),
                        segment=(entry.get("segments") or ["unknown"])[0],
                        response_text=f"[Error: {type(r).__name__}]",
                        sentiment="neutral",
                        response_time_ms=0,
                    )
                )

        elapsed = time.monotonic() - start
        logger.info(
            "Completed %d agents in %.1fs (avg %.0fms/agent, %d failures)",
            total,
            elapsed,
            (elapsed / total * 1000) if total else 0,
            failures,
        )

        return responses
