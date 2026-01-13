#!/usr/bin/env python3
"""
Kaggle Profile Badge Generator
Uses manual configuration since Kaggle blocks automated scraping.
Update the PROFILE_DATA dict below with your current stats.
"""

import json
from pathlib import Path

# Manual configuration - update these values when your stats change
PROFILE_DATA = {
    "username": "kakuteki",
    "competitions": {
        "tier": "Novice",
        "rank": None,
        "medals": {"gold": 0, "silver": 0, "bronze": 0}
    },
    "datasets": {
        "tier": "Novice",
        "rank": None,
        "medals": {"gold": 0, "silver": 0, "bronze": 0}
    },
    "notebooks": {
        "tier": "Expert",
        "rank": "463",
        "medals": {"gold": 0, "silver": 1, "bronze": 17}
    },
    "discussions": {
        "tier": "Novice",
        "rank": None,
        "medals": {"gold": 0, "silver": 0, "bronze": 0}
    },
}


def generate_svg(cat, tier, rank, medals):
    tier_colors = {
        "Grandmaster": "#d4af37",
        "Master": "#ff8c00",
        "Expert": "#9370db",
        "Contributor": "#32cd32",
        "Novice": "#20beff"
    }
    c = tier_colors.get(tier, "#20beff")
    g, s, b = medals.get("gold", 0), medals.get("silver", 0), medals.get("bronze", 0)
    
    # Build medal icons section
    medal_icons = ""
    x_pos = 70
    
    if g > 0:
        medal_icons += f'''<circle cx="{x_pos}" cy="66" r="7" fill="#FFD700"/>
<text x="{x_pos}" y="69" font-family="Arial" font-size="8" fill="#1a1a2e" text-anchor="middle" font-weight="bold">{g}</text>'''
        x_pos += 22
    
    if s > 0:
        medal_icons += f'''<circle cx="{x_pos}" cy="66" r="7" fill="#C0C0C0"/>
<text x="{x_pos}" y="69" font-family="Arial" font-size="8" fill="#1a1a2e" text-anchor="middle" font-weight="bold">{s}</text>'''
        x_pos += 22
    
    if b > 0:
        medal_icons += f'''<circle cx="{x_pos}" cy="66" r="7" fill="#CD7F32"/>
<text x="{x_pos}" y="69" font-family="Arial" font-size="8" fill="#1a1a2e" text-anchor="middle" font-weight="bold">{b}</text>'''
        x_pos += 22
    
    # Rank display
    rank_text = f'<text x="200" y="48" font-family="Arial" font-size="14" fill="#aaa" text-anchor="end">#{rank}</text>' if rank else ""
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="220" height="80">
<defs>
<linearGradient id="bg_{cat}" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#1a1a2e"/><stop offset="100%" style="stop-color:#16213e"/>
</linearGradient>
</defs>
<rect width="220" height="80" rx="10" fill="url(#bg_{cat})" stroke="{c}" stroke-width="2"/>
<circle cx="35" cy="40" r="20" fill="{c}" opacity="0.2"/>
<text x="35" y="46" font-family="Arial" font-size="20" fill="{c}" text-anchor="middle">K</text>
<text x="70" y="25" font-family="Arial" font-size="12" fill="#888">{cat.upper()}</text>
<text x="70" y="48" font-family="Arial" font-size="18" font-weight="bold" fill="{c}">{tier}</text>
{rank_text}
{medal_icons}
</svg>"""
    return svg


def main():
    out = Path("kaggle-badges")
    out.mkdir(exist_ok=True)
    
    print(f"Generating badges for: {PROFILE_DATA['username']}")
    
    with open(out / "profile_data.json", "w") as f:
        json.dump(PROFILE_DATA, f, indent=2)
    
    print(json.dumps(PROFILE_DATA, indent=2))
    
    for cat in ["competitions", "datasets", "notebooks", "discussions"]:
        d = PROFILE_DATA[cat]
        svg = generate_svg(cat, d["tier"], d["rank"], d["medals"])
        with open(out / f"{cat}.svg", "w") as f:
            f.write(svg)
        print(f"Generated: {cat}.svg")


if __name__ == "__main__":
    main()
