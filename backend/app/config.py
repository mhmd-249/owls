import os

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
AGENT_MODEL: str = os.getenv("AGENT_MODEL", "claude-sonnet-4-20250514")
AGGREGATION_MODEL: str = os.getenv("AGGREGATION_MODEL", "claude-opus-4-20250514")
MAX_CONCURRENT_AGENTS: int = int(os.getenv("MAX_CONCURRENT_AGENTS", "50"))
MAX_AGENTS: int = int(os.getenv("MAX_AGENTS", "200"))
PROFILES_DIR: str = os.getenv("PROFILES_DIR", "data/profiles")
PROCESSED_DIR: str = os.getenv("PROCESSED_DIR", "data/processed")
