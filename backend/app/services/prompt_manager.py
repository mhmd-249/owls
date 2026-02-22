import os
from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
_template_cache: dict[str, str] = {}


def _load_template(name: str) -> str:
    """Load a prompt template file, using cache for repeated reads."""
    if name not in _template_cache:
        path = _PROMPTS_DIR / name
        _template_cache[name] = path.read_text()
    return _template_cache[name]


def format_agent_prompt(persona: str) -> str:
    """Wrap a persona description with the agent persona instructions template.

    If the persona already contains INSTRUCTIONS (from pre-generated files),
    return it as-is to avoid double-wrapping.
    """
    if "INSTRUCTIONS FOR RESPONDING:" in persona or "IMPORTANT INSTRUCTIONS:" in persona:
        return persona

    template = _load_template("agent_persona.txt")
    return template.replace("{persona_description}", persona)


def format_evaluation_prompt(product_desc: str) -> str:
    """Format the product evaluation user message."""
    template = _load_template("agent_evaluation.txt")
    return template.replace("{product_description}", product_desc)


def clear_cache() -> None:
    """Clear the template cache (useful for testing)."""
    _template_cache.clear()
