from pydantic import BaseModel, field_validator


class PurchaseItem(BaseModel):
    item_id: str = ""
    category: str
    subcategory: str = ""
    color: str = ""
    size: str = ""
    price: float
    date: str
    returned: bool = False
    return_reason: str | None = ""


class BrowsingBehavior(BaseModel):
    categories_viewed: list[str] = []
    time_spent_minutes: float = 0.0
    items_wishlisted: int = 0
    collections_browsed: list[str] = []
    search_queries: list[str] = []


class FeedbackItem(BaseModel):
    type: str  # "review", "complaint", "support_ticket", "survey"
    content: str
    date: str
    rating: int | None = None  # 1-5 scale if applicable


class CustomerPreferences(BaseModel):
    style: list[str] | str = []
    favorite_colors: list[str] = []
    price_sensitivity: str = "medium"  # "low", "medium", "high"
    brand_affinity: list[str] = []
    avoids: list[str] = []
    preferred_fit: str = ""
    sustainability_interest: bool = False
    sale_shopper: bool = False

    @field_validator("style", mode="before")
    @classmethod
    def normalize_style(cls, v: list[str] | str) -> list[str]:
        if isinstance(v, str):
            return [v]
        return v


class CustomerProfile(BaseModel):
    customer_id: str
    name: str
    age: int
    gender: str
    location: str
    purchase_history: list[PurchaseItem] = []
    browsing_behavior: BrowsingBehavior = BrowsingBehavior()
    feedback_history: list[FeedbackItem] = []
    preferences: CustomerPreferences = CustomerPreferences()
    segments: list[str] = []
    member_since: str = ""
    loyalty_tier: str = ""  # "basic", "silver", "gold", "platinum"
