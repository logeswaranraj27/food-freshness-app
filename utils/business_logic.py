from datetime import datetime

# ===== ZERO-WASTE CULINARY DATABASE =====
RECIPE_CATALOG = {
    "Banana": {
        "Unripe / Firm": {
            "title": "Crispy Green Banana Plantain Chips & Savory Stir-fry",
            "time": "15 mins",
            "desc": "Thinly slice firm bananas and pan-crisp with sea salt, turmeric, and black pepper for a crunchy prebiotic snack."
        },
        "Optimal Freshness (Peak Peak)": {
            "title": "Classic Fruit Salad & Protein Chia Parfait",
            "time": "5 mins",
            "desc": "Slice over greek yogurt with honey, chia seeds, and toasted almonds for sustained morning energy."
        },
        "Fully Ripe / Softening": {
            "title": "Golden Banana Oat Pancakes (No Added Sugar)",
            "time": "10 mins",
            "desc": "Mash with 1 cup rolled oats, 2 eggs, and cinnamon. Griddle until golden brown — naturally sweet and fluffy."
        },
        "Near Expiration / Bruised": {
            "title": "Artisanal Cinnamon Banana Bread & Freezer Smoothie Cubes",
            "time": "45 mins",
            "desc": "Peel and mash for rich caramelized banana bread, or freeze chunks in airtight bags for ultra-creamy smoothies."
        }
    },
    "Apple": {
        "Unripe / Firm": {
            "title": "Tangy Apple Slaw with Mustard Dressing",
            "time": "10 mins",
            "desc": "Julienne crisp tart apples with cabbage, carrots, and apple cider vinaigrette for a crunchy side dish."
        },
        "Optimal Freshness (Peak Peak)": {
            "title": "Crisp Apple & Walnut Goat Cheese Crostini",
            "time": "10 mins",
            "desc": "Layer crisp wafer-thin apple rounds over toasted sourdough with goat cheese, walnuts, and thyme honey."
        },
        "Fully Ripe / Softening": {
            "title": "Warm Slow-Simmered Apple Cinnamon Butter",
            "time": "25 mins",
            "desc": "Simmer peeled softened apples with cloves, cinnamon, and a splash of lemon until thick and spreadable."
        },
        "Near Expiration / Bruised": {
            "title": "Rustic Cast-Iron Apple Crisp with Rolled Oats",
            "time": "35 mins",
            "desc": "Toss bruised diced apples with brown sugar and nutmeg. Top with buttered oat crumble and bake until bubbling."
        }
    },
    "Orange": {
        "Optimal Freshness (Peak Peak)": {
            "title": "Fresh Cold-Pressed Vitamin-C Immunity Elixir",
            "time": "5 mins",
            "desc": "Press fresh oranges with ginger root, a pinch of turmeric, and sparkling mineral water."
        },
        "Fully Ripe / Softening": {
            "title": "Citrus Glazed Roasted Carrots or Poultry",
            "time": "30 mins",
            "desc": "Reduce orange juice with garlic, rosemary, and honey to glaze oven-roasted vegetables or proteins."
        },
        "Near Expiration / Bruised": {
            "title": "Zesty Golden Orange Marmalade & Candied Rind",
            "time": "40 mins",
            "desc": "Boil sliced peels and fruit with sugar until translucent for a gourmet breakfast spread."
        }
    },
    "Tomato": {
        "Optimal Freshness (Peak Peak)": {
            "title": "Authentic Caprese Salad with Buffalo Mozzarella",
            "time": "5 mins",
            "desc": "Slice firm ripe tomatoes with fresh basil leaves, extra virgin olive oil, and aged balsamic glaze."
        },
        "Fully Ripe / Softening": {
            "title": "Rustic Roasted Garlic & Basil Marinara Sauce",
            "time": "25 mins",
            "desc": "Roast softening tomatoes at 200°C with garlic, olive oil, and oregano, then blend into a rich pasta sauce."
        },
        "Near Expiration / Bruised": {
            "title": "Creamy Roasted Tomato & Herb Bisque",
            "time": "30 mins",
            "desc": "Simmer bruised tomatoes with vegetable broth, thyme, and cream. Serve warm with crusty sourdough bread."
        }
    },
    "Mango": {
        "Optimal Freshness (Peak Peak)": {
            "title": "Tropical Mango Coconut Sticky Rice Parfait",
            "time": "15 mins",
            "desc": "Diced juicy sweet mango layered with warm coconut milk sticky rice and toasted sesame seeds."
        },
        "Fully Ripe / Softening": {
            "title": "Spicy Mango Lime Habanero Salsa",
            "time": "10 mins",
            "desc": "Toss diced ripe mango with red onions, cilantro, jalapeno, and fresh lime juice for tacos and chips."
        },
        "Near Expiration / Bruised": {
            "title": "Quick Mango Chutney or Chilled Mango Lassi",
            "time": "20 mins",
            "desc": "Simmer softened mango pulp with vinegar, cumin, and mustard seeds for a gourmet savory condiment."
        }
    },
    "Generic Fruit / Produce": {
        "Optimal Freshness (Peak Peak)": {
            "title": "Garden Fresh Detox Salad Bowl",
            "time": "10 mins",
            "desc": "Toss fresh produce with mixed greens, toasted pumpkin seeds, and a zesty lemon-herb dressing."
        },
        "Fully Ripe / Softening": {
            "title": "Energizing Multi-Fruit Smoothie Bowl",
            "time": "5 mins",
            "desc": "Blend ripe produce with almond milk, Greek yogurt, and ice for a nutrient-dense vitamin boost."
        },
        "Near Expiration / Bruised": {
            "title": "Zero-Waste Fruit Compote or Freezer Preserves",
            "time": "20 mins",
            "desc": "Simmer with a dash of honey and lemon juice, then jar as a topping for oatmeal, pancakes, or waffles."
        }
    }
}


def get_recipe_recommendation(fruit_name: str, ripeness_stage: str) -> dict:
    """Returns curated zero-waste culinary recipes tailored to fruit condition."""
    catalog = RECIPE_CATALOG.get(fruit_name, RECIPE_CATALOG["Generic Fruit / Produce"])
    
    # Try exact match or nearest category
    for stage_key, recipe in catalog.items():
        if stage_key.lower().split()[0] in ripeness_stage.lower():
            return recipe
            
    # Default fallback to first recipe
    return next(iter(catalog.values()))


def calculate_dynamic_markdown(freshness_score: float, base_price: float = 3.0, currency_symbol: str = "$") -> dict:
    """
    Computes dynamic markdown discount recommendations for grocery inventory managers:
    - Fresh (85%+): 0% discount (Full retail price)
    - Good (70-84%): 15% markdown (Fast mover promotion)
    - Fair / Ripe (50-69%): 35% markdown (Quick-Sale discount)
    - Clearance (35-49%): 60% markdown (Flash Clearance / Zero-Loss recovery)
    - Spoiled (<35%): 100% loss (Recommend compost / remove from display)
    """
    if freshness_score >= 85:
        discount_pct = 0
        strategy = "Premium Full Price — High Demand Stock"
        badge_color = "#10b981"  # Emerald
    elif freshness_score >= 70:
        discount_pct = 15
        strategy = "Healthy Stock — Minor 15% Promo to accelerate velocity"
        badge_color = "#3b82f6"  # Blue
    elif freshness_score >= 50:
        discount_pct = 35
        strategy = "Ripe Item — Apply 35% Quick-Sale Markdown to clear shelf"
        badge_color = "#f59e0b"  # Amber
    elif freshness_score >= 35:
        discount_pct = 60
        strategy = "Flash Clearance — 60% Markdown to salvage inventory cost"
        badge_color = "#ef4444"  # Red
    else:
        discount_pct = 100
        strategy = "Unsaleable — Remove immediately to protect batch hygiene"
        badge_color = "#6b7280"  # Gray

    discounted_price = round(base_price * (1 - (discount_pct / 100)), 2)
    saved_revenue = round(base_price - discounted_price if discount_pct < 100 else 0.0, 2)
    salvaged_amount = round(discounted_price if discount_pct < 100 else 0.0, 2)

    return {
        "discount_percent": discount_pct,
        "discount_badge": f"{discount_pct}% OFF" if discount_pct > 0 else "FULL PRICE",
        "original_price": f"{currency_symbol}{base_price:.2f}",
        "suggested_price": f"{currency_symbol}{discounted_price:.2f}" if discount_pct < 100 else f"{currency_symbol}0.00 (Write-off)",
        "salvaged_amount_val": salvaged_amount,
        "strategy": strategy,
        "badge_color": badge_color
    }


def generate_html_audit_report(history_records: list, store_name: str = "FreshMart Central", inspector_name: str = "AI Automated Quality System") -> str:
    """Generates an official Quality Inspection Audit Report in clean printable HTML."""
    now_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    total_scans = len(history_records)
    fresh_count = sum(1 for r in history_records if r.get("label") == "Fresh")
    rotten_count = sum(1 for r in history_records if r.get("label") == "Rotten")
    fresh_pct = round((fresh_count / total_scans * 100), 1) if total_scans > 0 else 100

    rows_html = ""
    for idx, r in enumerate(history_records[:30], 1):
        status_color = "#10b981" if r.get("label") == "Fresh" else "#ef4444"
        rows_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">#{idx}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{r.get('timestamp', 'N/A')}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;"><strong>{r.get('emoji', '🍎')} {r.get('fruit_name', 'Fruit')}</strong></td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; color: {status_color}; font-weight: bold;">{r.get('label', 'N/A')}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{r.get('freshness_score', 0)}%</td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{r.get('days_to_rot', 0)} days</td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{r.get('suggested_discount', '0%')}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Food Freshness Quality Audit Report</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1f2937; margin: 40px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #10b981; padding-bottom: 20px; }}
            .badge {{ background: #ecfdf5; color: #065f46; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 14px; border: 1px solid #a7f3d0; }}
            .kpi-container {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }}
            .kpi-card {{ background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; text-align: center; }}
            .kpi-num {{ font-size: 24px; font-weight: 800; color: #111827; margin-top: 6px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }}
            th {{ background: #f3f4f6; padding: 12px 10px; text-align: left; border-bottom: 2px solid #d1d5db; color: #374151; }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; display: flex; justify-content: space-between; font-size: 12px; color: #6b7280; }}
            @media print {{ body {{ margin: 0; }} .no-print {{ display: none; }} }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1 style="margin: 0 0 6px 0; color: #111827;">🍎 FreshScan™ Quality Audit & Inventory Report</h1>
                <p style="margin: 0; color: #6b7280;">Certified Cloud Food Safety & Spoilage Prevention Assessment</p>
            </div>
            <div style="text-align: right;">
                <span class="badge">ISO-Grade Quality Audit</span>
                <p style="margin: 6px 0 0 0; font-size: 13px; color: #6b7280;">Generated: {now_str}</p>
            </div>
        </div>

        <div style="margin-top: 20px;">
            <p><strong>Facility / Store:</strong> {store_name} | <strong>Auditor:</strong> {inspector_name}</p>
        </div>

        <div class="kpi-container">
            <div class="kpi-card">
                <div style="font-size: 12px; color: #6b7280; text-transform: uppercase;">Total Inspected</div>
                <div class="kpi-num">{total_scans} units</div>
            </div>
            <div class="kpi-card">
                <div style="font-size: 12px; color: #6b7280; text-transform: uppercase;">Batch Quality Score</div>
                <div class="kpi-num" style="color: #10b981;">{fresh_pct}%</div>
            </div>
            <div class="kpi-card">
                <div style="font-size: 12px; color: #6b7280; text-transform: uppercase;">Fresh Pass</div>
                <div class="kpi-num" style="color: #10b981;">{fresh_count}</div>
            </div>
            <div class="kpi-card">
                <div style="font-size: 12px; color: #6b7280; text-transform: uppercase;">Flagged / Spoilage</div>
                <div class="kpi-num" style="color: #ef4444;">{rotten_count}</div>
            </div>
        </div>

        <h3 style="margin-top: 30px; margin-bottom: 10px;">Detailed Quality Telemetry Log</h3>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Scan Timestamp</th>
                    <th>Fruit & Variety</th>
                    <th>Safety Status</th>
                    <th>Freshness</th>
                    <th>Shelf Life</th>
                    <th>Markdown Strategy</th>
                </tr>
            </thead>
            <tbody>
                {rows_html if rows_html else '<tr><td colspan="7" style="text-align:center; padding: 20px;">No scan logs recorded yet.</td></tr>'}
            </tbody>
        </table>

        <div class="footer">
            <div>
                <p>Digital Signature: <strong>[VERIFIED CLOUD TELEMETRY KEY: #FS-2026-CLOUD]</strong></p>
            </div>
            <div>
                <p>AI Food Freshness Detection Platform &bull; Retail Intelligence Suite</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content
