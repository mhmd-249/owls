from pydantic import BaseModel


class TestRequest(BaseModel):
    product_description: str
    target_segments: list[str] | None = None


class AgentResponse(BaseModel):
    agent_id: str
    profile_name: str
    age: int
    segment: str
    response_text: str
    sentiment: str
    response_time_ms: float


class SentimentBreakdown(BaseModel):
    positive: int = 0
    neutral: int = 0
    negative: int = 0
    positive_pct: float = 0.0
    neutral_pct: float = 0.0
    negative_pct: float = 0.0


class SegmentData(BaseModel):
    segment_name: str
    count: int
    sentiment: str
    summary: str
    key_quotes: list[str] = []
    recommendation: str = ""


class InsightResults(BaseModel):
    executive_summary: str = ""
    sentiment_breakdown: SentimentBreakdown = SentimentBreakdown()
    segments: list[SegmentData] = []
    key_themes: list[str] = []
    total_agents: int = 0
    response_rate: float = 0.0


class TestSession(BaseModel):
    test_id: str
    status: str = "pending"
    product_description: str = ""
    responses: list[AgentResponse] = []
    created_at: str = ""
