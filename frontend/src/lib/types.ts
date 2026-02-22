export interface AgentResponse {
  agent_id: string;
  profile_name: string;
  age: number;
  segment: string;
  response_text: string;
  sentiment: "positive" | "negative" | "neutral";
  response_time_ms: number;
}

export interface TestSession {
  test_id: string;
  status: "pending" | "running" | "aggregating" | "complete" | "error";
  product_description: string;
  responses: AgentResponse[];
  created_at: string;
}

export interface SentimentBreakdown {
  positive: number;
  neutral: number;
  negative: number;
  positive_pct: number;
  neutral_pct: number;
  negative_pct: number;
}

export interface SegmentData {
  segment_name: string;
  count: number;
  sentiment: "positive" | "mixed" | "negative";
  summary: string;
  key_quotes: string[];
  recommendation: string;
}

export interface InsightResults {
  executive_summary: string;
  sentiment_breakdown: SentimentBreakdown;
  segments: SegmentData[];
  key_themes: string[];
  total_agents: number;
  response_rate: number;
}

export interface CustomerProfile {
  customer_id: string;
  name: string;
  age: number;
  gender: string;
  location: string;
  purchase_history: PurchaseItem[];
  browsing_behavior: BrowsingBehavior;
  feedback_history: FeedbackItem[];
  preferences: CustomerPreferences;
  segments: string[];
}

interface PurchaseItem {
  category: string;
  subcategory: string;
  color: string;
  size: string;
  price: number;
  date: string;
}

interface BrowsingBehavior {
  categories_viewed: string[];
  time_spent_minutes: number;
  items_wishlisted: number;
}

interface FeedbackItem {
  type: "review" | "complaint" | "support_ticket";
  content: string;
  date: string;
}

interface CustomerPreferences {
  style: string[];
  price_sensitivity: "low" | "medium" | "high";
  brand_affinity: string[];
}
