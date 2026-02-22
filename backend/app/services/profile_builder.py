import json
import os
from collections import Counter
from pathlib import Path

from app.models.profile import CustomerProfile


def load_raw_profiles(data_dir: str) -> list[CustomerProfile]:
    """Load all customer profile JSON files from a directory."""
    profiles: list[CustomerProfile] = []
    data_path = Path(data_dir)

    for file_path in sorted(data_path.glob("customer_*.json")):
        with open(file_path) as f:
            data = json.load(f)
        profiles.append(CustomerProfile(**data))

    return profiles


def generate_persona_prompt(profile: CustomerProfile) -> str:
    """Transform a customer profile into a rich, natural-language persona description.

    This is the critical function — the persona must read like a character description
    and capture the customer's authentic voice, preferences, and behavior patterns.
    """
    parts: list[str] = []

    # Opening identity
    parts.append(
        f"You are {profile.name}, a {profile.age}-year-old {profile.gender} "
        f"living in {profile.location}."
    )

    # Membership context
    if profile.member_since:
        parts.append(
            f"You've been an H&M member since {profile.member_since[:4]}"
            + (f" ({profile.loyalty_tier} tier)." if profile.loyalty_tier else ".")
        )

    # Purchase history summary
    purchases = profile.purchase_history
    if purchases:
        total_items = len(purchases)
        total_spent = sum(p.price for p in purchases)
        avg_order = total_spent / total_items if total_items else 0

        # Category breakdown
        categories = Counter(p.category for p in purchases)
        top_categories = categories.most_common(3)
        cat_str = ", ".join(f"{cat} ({count})" for cat, count in top_categories)

        # Color breakdown
        colors = Counter(p.color.lower() for p in purchases if p.color)
        top_colors = [c for c, _ in colors.most_common(4)]

        parts.append(
            f"Over the past year, you've purchased {total_items} items "
            f"totaling around €{total_spent:.0f}, with an average of "
            f"€{avg_order:.0f} per item."
        )
        parts.append(f"Your shopping leans toward: {cat_str}.")

        if top_colors:
            parts.append(
                f"Your wardrobe palette favors {', '.join(top_colors)}."
            )

        # Specific item highlights
        subcategories = [p.subcategory for p in purchases if p.subcategory]
        if subcategories:
            unique_subs = list(dict.fromkeys(subcategories))[:5]
            parts.append(
                f"Recent purchases include: {', '.join(unique_subs)}."
            )

        # Returns
        returns = [p for p in purchases if p.returned]
        if returns:
            return_reasons = [
                r.return_reason for r in returns if r.return_reason
            ]
            parts.append(
                f"You returned {len(returns)} item(s)"
                + (
                    f" — reasons included: \"{return_reasons[0]}\""
                    if return_reasons
                    else ""
                )
                + "."
            )

    # Price sensitivity and shopping behavior
    prefs = profile.preferences
    if prefs.price_sensitivity == "high":
        parts.append(
            "You're price-conscious and look for good value."
        )
        if prefs.sale_shopper:
            parts.append("You primarily shop during sales and promotions.")
    elif prefs.price_sensitivity == "low":
        parts.append(
            "Price is not your primary concern — you prioritize quality and fit."
        )

    # Browsing behavior
    browsing = profile.browsing_behavior
    if browsing.categories_viewed:
        parts.append(
            f"You regularly browse {', '.join(browsing.categories_viewed[:4])} sections."
        )
    if browsing.items_wishlisted:
        parts.append(f"You currently have {browsing.items_wishlisted} items on your wishlist.")
    if browsing.collections_browsed:
        parts.append(
            f"Collections that caught your eye: {', '.join(browsing.collections_browsed[:3])}."
        )

    # Style and preferences
    styles = prefs.style if isinstance(prefs.style, list) else [prefs.style]
    if styles:
        parts.append(f"Your style is best described as {', '.join(styles)}.")
    if prefs.avoids:
        parts.append(f"You tend to avoid {', '.join(prefs.avoids[:3])}.")
    if prefs.preferred_fit:
        parts.append(f"You prefer a {prefs.preferred_fit} fit.")
    if prefs.sustainability_interest:
        parts.append(
            "Sustainability matters to you — you look for eco-friendly materials "
            "and ethical production."
        )
    if prefs.brand_affinity:
        parts.append(
            f"Beyond H&M, you also shop at {', '.join(prefs.brand_affinity[:3])}."
        )

    # Feedback voice — this captures the customer's authentic "voice"
    feedback = profile.feedback_history
    if feedback:
        for item in feedback[:2]:
            if item.type == "review":
                rating_note = f" (rated {item.rating}/5)" if item.rating else ""
                parts.append(f'In a recent review{rating_note}, you said: "{item.content}"')
            elif item.type == "complaint":
                parts.append(f'You once complained: "{item.content}"')
            elif item.type == "survey":
                parts.append(f'In a survey, you shared: "{item.content}"')
            elif item.type == "support_ticket":
                parts.append(f'You contacted support about: "{item.content}"')

    # Segment context
    if profile.segments:
        readable_segments = [s.replace("_", " ") for s in profile.segments]
        parts.append(
            f"You'd best be categorized as a {', '.join(readable_segments)} shopper."
        )

    return " ".join(parts)


def build_all_personas(profiles_dir: str, output_dir: str) -> dict:
    """Load all profiles, generate personas, save to files, and create manifest."""
    profiles = load_raw_profiles(profiles_dir)
    os.makedirs(output_dir, exist_ok=True)

    manifest: dict = {}

    for profile in profiles:
        persona_text = generate_persona_prompt(profile)

        # Save persona to individual text file
        filename = f"{profile.customer_id}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w") as f:
            f.write(persona_text)

        # Add to manifest
        manifest[profile.customer_id] = {
            "persona_file": filename,
            "name": profile.name,
            "age": profile.age,
            "gender": profile.gender,
            "location": profile.location,
            "segments": profile.segments,
            "loyalty_tier": profile.loyalty_tier,
            "total_purchases": len(profile.purchase_history),
        }

    # Save manifest
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest


