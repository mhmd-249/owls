import asyncio
import os
import time

from dotenv import load_dotenv

load_dotenv()

import pytest

from app.services.agent_runner import AgentRunner, detect_sentiment

PRODUCT_DESCRIPTION = (
    "H&M is launching a new line of oversized graphic t-shirts "
    "with vintage 90s designs, priced at €24.99"
)

_skip_no_key = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping live agent tests",
)


class TestDetectSentiment:
    """These tests don't need an API key."""

    def test_positive_sentiment(self) -> None:
        assert detect_sentiment("I love this! Would definitely buy it.") == "positive"

    def test_negative_sentiment(self) -> None:
        assert detect_sentiment("I wouldn't buy this, not interested at all.") == "negative"

    def test_neutral_sentiment(self) -> None:
        assert detect_sentiment("I could see it working for some people.") == "neutral"

    def test_mixed_leans_positive(self) -> None:
        text = "I love the concept but don't like the price."
        result = detect_sentiment(text)
        assert result in ("positive", "neutral")

    def test_case_insensitive(self) -> None:
        assert detect_sentiment("LOVE this, AMAZING design!") == "positive"


@_skip_no_key
class TestAgentRunnerLive:
    """Live API tests — run 5 agents against a product description."""

    @pytest.fixture
    def runner(self) -> AgentRunner:
        return AgentRunner(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            model=os.getenv("AGENT_MODEL", "claude-sonnet-4-20250514"),
            max_concurrent=5,
        )

    def test_run_5_agents(self, runner: AgentRunner) -> None:
        """Run 5 agents and verify responses are realistic and timely."""
        start = time.time()
        responses = asyncio.run(
            runner.run_all_agents(
                product_description=PRODUCT_DESCRIPTION,
                processed_dir="data/processed",
                max_agents=5,
            )
        )
        elapsed = time.time() - start

        # Should have exactly 5 responses
        assert len(responses) == 5, f"Expected 5 responses, got {len(responses)}"

        # Should complete within 30 seconds
        assert elapsed < 30, f"Took {elapsed:.1f}s, expected under 30s"

        # Print responses for manual review
        print(f"\n{'='*60}")
        print(f"5 AGENT RESPONSES ({elapsed:.1f}s total)")
        print(f"{'='*60}")

        for r in responses:
            print(f"\n--- {r.profile_name} (age {r.age}, {r.segment}) ---")
            print(f"Sentiment: {r.sentiment} | Time: {r.response_time_ms:.0f}ms")
            print(f"Response: {r.response_text}")

        # Verify all responses are real (not errors)
        errors = [r for r in responses if r.response_text.startswith("[Error:")]
        assert len(errors) == 0, f"{len(errors)} agents failed: {errors}"

        # Verify responses have meaningful content
        for r in responses:
            assert len(r.response_text) > 20, (
                f"Response from {r.profile_name} too short: {r.response_text!r}"
            )

        # Verify sentiment labels are valid
        for r in responses:
            assert r.sentiment in ("positive", "negative", "neutral"), (
                f"Invalid sentiment {r.sentiment!r} for {r.profile_name}"
            )

    def test_single_agent_with_callback(self, runner: AgentRunner) -> None:
        """Verify the callback mechanism works for SSE streaming."""
        received: list = []

        async def on_done(response: object) -> None:
            received.append(response)

        asyncio.run(
            runner.run_all_agents(
                product_description=PRODUCT_DESCRIPTION,
                processed_dir="data/processed",
                max_agents=3,
                callback=on_done,
            )
        )

        assert len(received) == 3, f"Callback received {len(received)} responses, expected 3"
