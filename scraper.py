# scraper.py
import re
import requests
from slugify import slugify
from markdownify import markdownify as md

BASE_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"

def clean_to_markdown(html_content: str, domain: str = "https://support.optisigns.com") -> str:
    if not html_content:
        return ""
    # Chuyển link nội bộ thành relative link
    html_content = html_content.replace(domain, "")
    
    # Strip script/style/forms và format heading ATX
    markdown = md(
        html_content,
        heading_style="ATX",
        strip=["script", "style", "form", "iframe"]
    )
    return re.sub(r'\n{3,}', '\n\n', markdown).strip()

def fetch_articles(limit: int = 35) -> list:
    articles = []
    url = f"{BASE_URL}?per_page=30"
    
    while url and len(articles) < limit:
        res = requests.get(url, headers={"User-Agent": "OptiBot-Sync/1.0"}, timeout=15)
        if res.status_code != 200:
            break
        data = res.json()
        for item in data.get("articles", []):
            if len(articles) >= limit:
                break
            
            clean_md = clean_to_markdown(item.get("body", ""))
            slug = slugify(item.get("title", f"article-{item['id']}"))
            
            articles.append({
                "id": str(item["id"]),
                "title": item.get("title", ""),
                "slug": slug,
                "url": item.get("html_url", ""),
                "updated_at": item.get("updated_at", ""),
                "markdown": clean_md
            })
        url = data.get("next_page")
        
    return articles