"""
Real H&M Data → Persona Prompt Converter

This script replaces the synthetic profile builder from Phase 1.
It reads the real H&M customer data CSV and generates rich persona prompts
by combining the lifestyle Summary with actual purchase history.

Usage:
    python convert_real_data.py --input H_M_persona_data.csv --output backend/data/processed/

Output:
    - One .txt persona file per customer in the output directory
    - manifest.json mapping customer_id → persona file path + demographics
"""

import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime


def load_and_group_data(csv_path: str) -> dict:
    """Load CSV and group rows by customer_id."""
    customers = defaultdict(lambda: {"summary": "", "age": 0, "purchases": []})
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row["customer_id"]
            customers[cid]["summary"] = row["Summary"]
            customers[cid]["age"] = int(float(row["age"])) if row["age"] else 0
            customers[cid]["club_member_status"] = row.get("club_member_status", "")
            customers[cid]["purchases"].append({
                "product_name": row["prod_name"],
                "product_type": row["product_type_name"],
                "product_group": row["product_group_name"],
                "color": row["colour_group_name"],
                "perceived_color": row["perceived_colour_value_name"],
                "department": row["department_name"],
                "index_name": row["index_name"],
                "section": row["section_name"],
                "garment_group": row["garment_group_name"],
                "detail_desc": row["detail_desc"],
                "date": row["t_dat"],
                "price": float(row["price"]) if row["price"] else 0,
                "channel": "Online" if row.get("sales_channel_id") == "2" else "In-store",
            })
    
    return dict(customers)


def build_purchase_summary(purchases: list) -> str:
    """Create a natural-language shopping history from purchase rows."""
    if not purchases:
        return "No purchase history available."
    
    # Count by category
    categories = defaultdict(int)
    colors = defaultdict(int)
    departments = defaultdict(int)
    total_spent = 0
    channels = defaultdict(int)
    dates = []
    
    for p in purchases:
        categories[p["product_group"]] += 1
        colors[p["color"]] += 1
        departments[p["department"]] += 1
        total_spent += p["price"]
        channels[p["channel"]] += 1
        if p["date"]:
            dates.append(p["date"])
    
    # Sort by frequency
    top_categories = sorted(categories.items(), key=lambda x: -x[1])
    top_colors = sorted(colors.items(), key=lambda x: -x[1])
    top_departments = sorted(departments.items(), key=lambda x: -x[1])
    
    # Date range
    if dates:
        dates_sorted = sorted(dates)
        date_range = f"from {dates_sorted[0]} to {dates_sorted[-1]}"
    else:
        date_range = "over an unknown period"
    
    # Primary channel
    primary_channel = max(channels.items(), key=lambda x: x[1])[0] if channels else "Unknown"
    
    # Build narrative
    lines = []
    lines.append(f"SHOPPING HISTORY AT H&M ({len(purchases)} items purchased {date_range}):")
    
    # Categories
    cat_parts = [f"{name} ({count})" for name, count in top_categories[:5]]
    lines.append(f"- Main categories: {', '.join(cat_parts)}")
    
    # Colors
    color_parts = [f"{name} ({count})" for name, count in top_colors[:5]]
    lines.append(f"- Preferred colors: {', '.join(color_parts)}")
    
    # Departments
    dept_parts = [f"{name}" for name, count in top_departments[:4]]
    lines.append(f"- Shops in departments: {', '.join(dept_parts)}")
    
    # Channel
    lines.append(f"- Shopping channel: primarily {primary_channel}")
    
    # Specific recent purchases (last 5)
    recent = sorted(purchases, key=lambda x: x["date"] or "", reverse=True)[:5]
    lines.append("- Recent purchases:")
    for p in recent:
        lines.append(f"  • {p['product_name']} ({p['color']}, {p['product_type']}) — {p['date']}")
    
    return "\n".join(lines)


def generate_persona_prompt(customer_data: dict) -> str:
    """Combine Summary + purchase history into a final persona prompt."""
    summary = customer_data["summary"].strip()
    purchase_summary = build_purchase_summary(customer_data["purchases"])
    
    persona = f"""{summary}

---

{purchase_summary}

---

INSTRUCTIONS FOR RESPONDING:
- You ARE this person. Respond naturally as yourself, in first person.
- When presented with a product idea from H&M, react authentically based on your personality, lifestyle, shopping habits, and preferences described above.
- Be specific: mention what you like, dislike, what would make you buy or not buy.
- Reference your past experiences with similar products when relevant.
- Your response should reflect your unique perspective — your age, location, lifestyle, and values.
- Keep your response to 3-5 sentences. Be conversational, not formal.
- If the product isn't relevant to you at all, say so and explain why."""

    return persona


def generate_short_name(customer_id: str, index: int) -> str:
    """Generate a display name from index."""
    names = [
        "Alex", "Sam", "Jordan", "Morgan", "Riley", "Casey", "Taylor", "Quinn",
        "Avery", "Reese", "Dakota", "Sage", "Rowan", "Finley", "Harper", "Blair",
        "Emerson", "Skyler", "Phoenix", "Drew"
    ]
    return names[index % len(names)]


def infer_segments(customer_data: dict) -> list:
    """Infer customer segments from their data."""
    segments = []
    purchases = customer_data["purchases"]
    age = customer_data["age"]
    
    # Age-based
    if age < 25:
        segments.append("young_adult")
    elif age < 40:
        segments.append("adult")
    elif age < 55:
        segments.append("mature")
    else:
        segments.append("senior")
    
    # Purchase frequency
    if len(purchases) > 20:
        segments.append("frequent_shopper")
    elif len(purchases) > 5:
        segments.append("regular_shopper")
    else:
        segments.append("occasional_shopper")
    
    # Category-based
    categories = [p["product_group"] for p in purchases]
    if any("Upper" in c for c in categories):
        segments.append("tops_buyer")
    if any("Lower" in c for c in categories):
        segments.append("bottoms_buyer")
    if any("Full" in c for c in categories):
        segments.append("fullbody_buyer")
    
    return segments


def convert_all(csv_path: str, output_dir: str):
    """Main conversion: CSV → persona files + manifest."""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading data from {csv_path}...")
    customers = load_and_group_data(csv_path)
    print(f"Found {len(customers)} unique customers")
    
    manifest = {}
    
    for idx, (customer_id, data) in enumerate(customers.items()):
        display_name = generate_short_name(customer_id, idx)
        persona_prompt = generate_persona_prompt(data)
        segments = infer_segments(data)
        
        # Save persona file
        filename = f"persona_{idx:03d}_{display_name.lower()}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(persona_prompt)
        
        # Add to manifest
        manifest[customer_id] = {
            "persona_file": filepath,
            "display_name": display_name,
            "age": data["age"],
            "purchase_count": len(data["purchases"]),
            "segments": segments,
            "club_member_status": data.get("club_member_status", ""),
        }
        
        print(f"  [{idx+1}/{len(customers)}] {display_name} (age {data['age']}, {len(data['purchases'])} purchases, {len(persona_prompt)} chars)")
    
    # Save manifest
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nDone! {len(customers)} personas saved to {output_dir}")
    print(f"Manifest saved to {manifest_path}")
    
    return manifest


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert H&M data to persona prompts")
    parser.add_argument("--input", default="H_M_persona_data.csv", help="Path to CSV file")
    parser.add_argument("--output", default="backend/data/processed/", help="Output directory")
    args = parser.parse_args()
    
    convert_all(args.input, args.output)