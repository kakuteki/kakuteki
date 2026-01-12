#!/usr/bin/env python3
"""
Kaggle Profile Scraper
Scrapes Kaggle profile data and generates SVG badges
"""

import json
import os
import re
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing playwright...")
    os.system("pip install playwright")
    os.system("playwright install chromium")
    from playwright.sync_api import sync_playwright


def scrape_kaggle_profile(username: str) -> dict:
    """Scrape Kaggle profile data using Playwright"""
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
        page = browser.new_page()
        
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)  # Wait for dynamic content
            
            # Get page content
            content = page.content()
            
            # Try to find tier/rank information from the page
            # Kaggle stores data in script tags or data attributes
            
            # Look for tier badges
            tier_patterns = {
                "grandmaster": "Grandmaster",
                "master": "Master", 
                "expert": "Expert",
                "contributor": "Contributor",
                "novice": "Novice"
            }
            
            # Extract tier info from page content
            categories = ["competitions", "datasets", "notebooks", "discussions"]
            
            for category in categories:
                # Look for tier mentions near category names
                cat_pattern = rf'{category}[^<]*?(?:tier|rank)[^<]*?(\w+)'
                match = re.search(cat_pattern, content.lower())
                if match:
                    tier_text = match.group(1)
                    for key, value in tier_patterns.items():
                        if key in tier_text:
                            profile_data[category]["tier"] = value
                            break
            
            # Try to extract medal counts
            # Look for medal icons/counts in the page
            medal_pattern = r'(\d+)\s*(?:gold|silver|bronze)'
            
            # Get all text content for analysis
            text_content = page.inner_text("body")
            
            # Look for ranking information
            rank_pattern = r'(?:rank|#)\s*(\d{1,6})'
            rank_matches = re.findall(rank_pattern, text_content.lower())
            if rank_matches:
                profile_data["competitions"]["rank"] = rank_matches[0]
            
            # Try to get data from Kaggle's internal JSON
            scripts = page.query_selector_all("script")
            for script in scripts:
                script_content = script.inner_html()
                if "userProfile" in script_content or "competitions" in script_content:
                    # Try to extract JSON data
                    json_match = re.search(r'\{[^{}]*"tier"[^{}]*\}', script_content)
                    if json_match:
                        try:
                            data = json.loads(json_match.group())
                            # Process extracted data
                        except:
                            pass
            
        except Exception as e:
            print(f"Error scraping profile: {e}")
        finally:
            browser.close()
    
    return profile_data


def generate_svg_badge(category: str, tier: str, rank: str = None, medals: dict = None) -> str:
    """Generate an SVG badge for a Kaggle category"""
    
    # Tier colors
    tier_colors = {
        "Grandmaster": "#d4af37",  # Gold
        "Master": "#ff8c00",       # Orange
        "Expert": "#9370db",       # Purple
        "Contributor": "#32cd32",  # Green
        "Novice": "#4a90d9"        # Blue
    }
    
    color = tier_colors.get(tier, "#4a90d9")
    
    # Medal counts
    gold = medals.get("gold", 0) if medals else 0
    silver = medals.get("silver", 0) if medals else 0
    bronze = medals.get("bronze", 0) if medals else 0
    
    rank_text = f"#{rank}" if rank else ""
    medal_text = f"🥇{gold} 🥈{silver} 🥉{bronze}" if any([gold, silver, bronze]) else ""
    
    width = 200
    height = 80
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="bg_{category}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#16213e;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="{width}" height="{height}" rx="10" fill="url(#bg_{category})" stroke="{color}" stroke-width="2"/>
  
  <!-- Kaggle Logo Area -->
  <circle cx="35" cy="40" r="20" fill="{color}" opacity="0.2"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-size="20" fill="{color}" text-anchor="middle">K</text>
  
  <!-- Category Name -->
  <text x="70" y="25" font-family="Arial, sans-serif" font-size="12" fill="#888888">{category.upper()}</text>
  
  <!-- Tier -->
  <text x="70" y="45" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="{color}">{tier}</text>
  
  <!-- Rank -->
  <text x="70" y="65" font-family="Arial, sans-serif" font-size="11" fill="#aaaaaa">{rank_text} {medal_text}</text>
</svg>'''
    
    return svg


def main():
    username = os.environ.get("KAGGLE_USERNAME", "kakuteki")
    output_dir = Path("kaggle-badges")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Scraping Kaggle profile for: {username}")
    

    # Scrape profile data (for debugging)
    scraped_data = scrape_kaggle_profile(username)
    print(f"Scraped data: {json.dumps(scraped_data, indent=2)}")

    # Use accurate data provided by user
    profile_data = {
        "username": username,
        "competitions": {"tier": "Novice", "rank": "403", "medals": {"gold": 0, "silver": 0, "bronze": 0}},
        "datasets": {"tier": "Novice", "rank": None, "medals": {"gold": 0, "silver": 0, "bronze": 0}},
        "notebooks": {"tier": "Expert", "rank": "463", "medals": {"gold": 0, "silver": 1, "bronze": 17}},
        "discussions": {"tier": "Novice", "rank": None, "medals": {"gold": 0, "silver": 0, "bronze": 0}},
    }

    with open(output_dir / "profile_data.json", "w") as f:
        json.dump(profile_data, f, indent=2)
    
    print(f"Profile data: {json.dumps(profile_data, indent=2)}")
    
    # Generate badges
    categories = ["competitions", "datasets", "notebooks", "discussions"]
    
    for category in categories:
        data = profile_data.get(category, {})
        tier = data.get("tier", "Novice")
        rank = data.get("rank")
        medals = data.get("medals", {})
        
        svg = generate_svg_badge(category, tier, rank, medals)
        
        badge_path = output_dir / f"{category}.svg"
        with open(badge_path, "w") as f:
            f.write(svg)
        
        print(f"Generated: {badge_path}")
    
    print("Done!")


if __name__ == "__main__":
    main()
