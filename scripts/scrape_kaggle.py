#!/usr/bin/env python3
"""
Kaggle Profile Scraper - Dynamic Version
"""

import json
import os
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    os.system("pip install playwright")
    os.system("playwright install chromium")
    from playwright.sync_api import sync_playwright


def scrape_kaggle_profile(username):
    profile_data = {
        "username": username,
        "competitions": {"tier": "Novice", "rank": None, "medals": {"gold": 0, "silver": 0, "bronze": 0}},
        "datasets": {"tier": "Novice", "rank": None, "medals": {"gold": 0, "silver": 0, "bronze": 0}},
        "notebooks": {"tier": "Novice", "rank": None, "medals": {"gold": 0, "silver": 0, "bronze": 0}},
        "discussions": {"tier": "Novice", "rank": None, "medals": {"gold": 0, "silver": 0, "bronze": 0}},
    }

    url = f"https://www.kaggle.com/{username}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120")
        page = context.new_page()

        try:
            print(f"Loading {url}...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)

            body_text = page.inner_text("body")
            print(f"Page length: {len(body_text)}")

            Path("kaggle-badges").mkdir(exist_ok=True)
            with open("kaggle-badges/debug.txt", "w", encoding="utf-8") as f:
                f.write(body_text)

            cats = {"Competition": "competitions", "Dataset": "datasets", "Notebook": "notebooks", "Discussion": "discussions"}
            tiers = ["Grandmaster", "Master", "Expert", "Contributor", "Novice"]

            lines = [l.strip() for l in body_text.split("\n") if l.strip()]

            for i, line in enumerate(lines):
                if line in tiers:
                    for j in range(max(0, i-5), min(len(lines), i+5)):
                        for cat_name, cat_key in cats.items():
                            if cat_name in lines[j]:
                                profile_data[cat_key]["tier"] = line
                                print(f"Tier: {cat_key}={line}")

            for i, line in enumerate(lines):
                if line == "Rank" and i+1 < len(lines):
                    rank = lines[i+1].replace(",", "")
                    if rank.isdigit():
                        for j in range(max(0, i-15), i):
                            for cat_name, cat_key in cats.items():
                                if cat_name in lines[j]:
                                    profile_data[cat_key]["rank"] = rank
                                    print(f"Rank: {cat_key}={rank}")

            for i, line in enumerate(lines):
                if line == "Medals":
                    cat_key = None
                    for j in range(i-1, max(0, i-20), -1):
                        for cat_name, ck in cats.items():
                            if cat_name in lines[j]:
                                cat_key = ck
                                break
                        if cat_key:
                            break

                    if cat_key:
                        g = s = b = 0
                        for j in range(i, min(len(lines), i+15)):
                            if lines[j].isdigit() and j+1 < len(lines):
                                n = int(lines[j])
                                nxt = lines[j+1].lower()
                                if "gold" in nxt: g = n
                                elif "silver" in nxt: s = n
                                elif "bronze" in nxt: b = n
                        if g or s or b:
                            profile_data[cat_key]["medals"] = {"gold": g, "silver": s, "bronze": b}
                            print(f"Medals: {cat_key}=G{g}S{s}B{b}")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

    return profile_data


def generate_svg(cat, tier, rank, medals):
    colors = {"Grandmaster": "#d4af37", "Master": "#ff8c00", "Expert": "#9370db", "Contributor": "#32cd32", "Novice": "#20beff"}
    c = colors.get(tier, "#20beff")
    g, s, b = medals.get("gold", 0), medals.get("silver", 0), medals.get("bronze", 0)
    r = f"#{rank}" if rank else ""
    m = " ".join([f"G{g}" if g else "", f"S{s}" if s else "", f"B{b}" if b else ""]).strip()
    info = " ".join(filter(None, [r, m]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="220" height="80">
<defs><linearGradient id="bg_{cat}" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#1a1a2e"/><stop offset="100%" style="stop-color:#16213e"/></linearGradient></defs>
<rect width="220" height="80" rx="10" fill="url(#bg_{cat})" stroke="{c}" stroke-width="2"/>
<circle cx="35" cy="40" r="20" fill="{c}" opacity="0.2"/>
<text x="35" y="46" font-family="Arial" font-size="20" fill="{c}" text-anchor="middle">K</text>
<text x="70" y="25" font-family="Arial" font-size="12" fill="#888">{cat.upper()}</text>
<text x="70" y="48" font-family="Arial" font-size="18" font-weight="bold" fill="{c}">{tier}</text>
<text x="70" y="68" font-family="Arial" font-size="11" fill="#aaa">{info}</text>
</svg>'''


def main():
    user = os.environ.get("KAGGLE_USERNAME", "kakuteki")
    out = Path("kaggle-badges")
    out.mkdir(exist_ok=True)

    print(f"Scraping: {user}")
    data = scrape_kaggle_profile(user)

    with open(out / "profile_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print(json.dumps(data, indent=2))

    for cat in ["competitions", "datasets", "notebooks", "discussions"]:
        d = data[cat]
        svg = generate_svg(cat, d["tier"], d["rank"], d["medals"])
        with open(out / f"{cat}.svg", "w") as f:
            f.write(svg)
        print(f"Generated: {cat}.svg")


if __name__ == "__main__":
    main()
