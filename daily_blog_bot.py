
import os
import json
import time
import feedparser
from datetime import datetime, timedelta
from openai import OpenAI
from supabase import create_client, Client
import re
from bs4 import BeautifulSoup

# ==========================================
# 🔧 用户控制面板 (USER CONTROL PANEL)
# ==========================================

# 1. RSS 订阅列表 (已更新为用户精选列表)
RSS_FEEDS = [
    "https://aws.amazon.com/blogs/aws/feed/", 
    "https://www.amazon.science/index.xml",
    "https://www.marketplacepulse.com/articles/recent.atom",
    "http://www.ecommercebytes.com/feed/",
    "https://www.helium10.com/blog/feed/",
    "https://www.junglescout.com/feed/",
    "https://www.sellerlabs.com/blog/feed/",
    "https://www.ecomengine.com/blog/rss.xml",
    "https://tamebay.com/feed",
    "https://retaildive.com/feeds/news/",
]

# 2. 只有最近 N 天的新闻才会被采用 (防止写出旧闻)
NEWS_MAX_AGE_DAYS = 2

# 3. 每天发布文章数量限制
LIMIT_POSTS_PER_RUN = 1

# 4. AI 模型选择
AI_MODEL_NAME = "anthropic/claude-3.5-sonnet"

# ==========================================
# ⚙️ 系统配置 (System Config) - 勿动
# ==========================================

# Initialize Clients
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
site_url = "https://amzaiagent.com"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
    default_headers={
        "HTTP-Referer": site_url,
        "X-Title": "Amz AI Agent Bot",
    },
)

try:
    if supabase_url and supabase_key:
        supabase: Client = create_client(supabase_url, supabase_key)
    else:
        print("Warning: Supabase credentials missing. DB save will be skipped.")
        supabase = None
except Exception as e:
    print(f"Supabase init warning: {e}")
    supabase = None

def clean_html(raw_html):
    CLEANR = re.compile('<.*?>') 
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext

def extract_image_from_entry(entry):
    """
    Attempt to extract the best image URL from an RSS entry.
    Priority:
    1. Media Content / Enclosures (Standard RSS)
    2. Parsing <img src> from description/summary (BeautifulSoup)
    3. None (Bot will use topic-based fallback later)
    """
    # 1. Check media_content or enclosures
    if hasattr(entry, 'media_content'):
        for media in entry.media_content:
            if media.get('type', '').startswith('image') or 'medium' in media:
                return media.get('url')
                
    if hasattr(entry, 'media_thumbnail'):
        for media in entry.media_thumbnail:
            return media.get('url')
            
    if hasattr(entry, 'enclosures'):
        for enclosure in entry.enclosures:
            if enclosure.get('type', '').startswith('image'):
                return enclosure.get('href')

    # 2. Parse HTML content for <img> tags
    content_html = ""
    if hasattr(entry, 'content'):
        content_html = entry.content[0].value
    elif hasattr(entry, 'summary'):
        content_html = entry.summary
    elif hasattr(entry, 'description'):
        content_html = entry.description
        
    if content_html:
        try:
            soup = BeautifulSoup(content_html, 'lxml')
            img_tag = soup.find('img')
            if img_tag and img_tag.get('src'):
                return img_tag.get('src')
        except Exception:
            pass
            
    return None

def fetch_and_filter_candidates():
    """
    Fetch news from ALL feeds and filter by date.
    Returns a list of valid candidate items.
    """
    print("Fetching RSS feeds from all sources...")
    candidates = []
    
    cutoff_date = datetime.now() - timedelta(days=NEWS_MAX_AGE_DAYS)
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            print(f"Checking {feed_url} - Found {len(feed.entries)} entries")
            
            for entry in feed.entries[:5]: 
                # Check date
                published_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_time = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
                
                if not published_time:
                    continue
                
                # Filter by age
                if published_time > cutoff_date:
                    # Extract Image
                    img_url = extract_image_from_entry(entry)
                    
                    candidates.append({
                        "source": feed.feed.get('title', 'Unknown Source'),
                        "title": entry.title,
                        "link": entry.link,
                        "summary": clean_html(getattr(entry, 'summary', '') or getattr(entry, 'description', ''))[:300],
                        "published": published_time.strftime("%Y-%m-%d"),
                        "image_url": img_url # Can be None
                    })
        except Exception as e:
            print(f"Error parsing {feed_url}: {e}")
            continue
            
    print(f"Total valid candidates found (last {NEWS_MAX_AGE_DAYS} days): {len(candidates)}")
    return candidates

def select_best_article(candidates):
    """
    Uses LLM to pick the best article from the list.
    """
    if not candidates:
        return None
        
    print("Asking AI to select the best topic...")
    
    candidates_list_str = ""
    for idx, item in enumerate(candidates):
        has_img = "✅" if item['image_url'] else "❌"
        candidates_list_str += f"[{idx}] Source: {item['source']} | Title: {item['title']} | Date: {item['published']} | Image: {has_img}\n"
        
    prompt = f"""
    You are an expert editor for "Amz AI Agent". Select the ONE most impactful news story for Amazon Sellers.
    
    Criteria:
    1. Relevance: Must impact Amazon FBA Sellers directly.
    2. Visuals: Prefer stories that have an Image (✅) if the quality/relevance is equal.
    3. Value: Strategic value over gossip.
    
    Candidate List:
    {candidates_list_str}
    
    Return ONLY JSON:
    {{
        "best_index": 0,
        "reason": "Explain why"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model=AI_MODEL_NAME, 
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        selection = json.loads(content.strip())
        best_idx = selection.get("best_index", 0)
        
        return candidates[best_idx]
        
    except Exception as e:
        print(f"AI Selection failed: {e}. Defaulting to first candidate.")
        return candidates[0]

def get_fallback_image(title, tags):
    """
    Return a relevant static placeholder if no real image found.
    Simple keyword matching.
    """
    t = title.lower()
    # These should exist in your project assets, or link to public placeholders
    if "ai" in t or "tech" in t or "robot" in t or "automated" in t:
        return "assets/images/blog/ai_tech_placeholder.jpg" # Example
    if "logistic" in t or "ship" in t or "delivery" in t or "fba" in t:
        return "assets/images/blog/logistics_placeholder.jpg"
    if "policy" in t or "rule" in t or "law" in t or "ban" in t:
        return "assets/images/blog/policy_placeholder.jpg"
    
    return "images/blog_thumbs/default_news.png"

def generate_blog_post(news_item):
    """Uses LLM to write a blog post based on the selected news."""
    print(f"Generating content for: {news_item['title']}...")
    
    prompt = f"""
    You are an expert Amazon FBA consultant and SEO Strategist (E-E-A-T compliant). 
    Your goal is to write a world-class blog post that ranks #1 on Google.
    
    Source Material:
    - Title: {news_item['title']}
    - Summary: {news_item['summary']}
    - Link: {news_item['link']}
    
    ==================================================
    MANDATORY SEO REQUIREMENTS (Strict Enforcement)
    ==================================================
    
    1. 🔍 **Keyword Strategy**:
       - Primary Keyword: Identify the most searchable term related to this news (e.g., "Amazon FBA Fee Change 2026").
       - Placement: Must appear in the **First H1 Title**, **First Paragraph (first 100 words)**, and **at least one H2**.
    
    2. 🔗 **Internal Linking Strategy**:
       - You MUST contextually link to at least 2 internal pages if relevant:
         - <a href="/index.html">Amz AI Agent Home</a> (for general tools)
         - <a href="/faq.html">FBA FAQ</a> (for questions)
         - <a href="/about.html">About Us</a>
       - Do NOT force them; weave them naturally into the text (e.g., "Use tools like <a href='/index.html'>Amz AI Agent</a> to monitor these changes...").
    
    3. 🖼️ **Image Optimization**:
       - If you insert the image, the `<img>` tag MUST have a descriptive `alt` attribute containing the Primary Keyword.
       - Syntax: <img src="{news_item['image_url'] or 'PLACEHOLDER'}" alt="[Primary Keyword] - Descriptive Text" class="rounded-lg my-4 w-full object-cover">
    
    4. 🧩 **Structure & Readability**:
       - **H1**: High-impact title.
       - **Intro**: Hook the reader immediately. State the "What" and "Why".
       - **H2**: Deep dive into the details.
       - **H2**: Impact on Sellers (The "So What?").
       - **H2**: 3 Actionable Steps (Bulleted list).
       - **H2**: Frequently Asked Questions (FAQ) - **Crucial for SEO Snippets**.
         - Write 3 Q&A pairs related to the news.
       - **Conclusion**: Brief summary + Call to Action (CTA).
    
    5. 📣 **Engagement**:
       - End with a question to encourage comments.
    
    Output JSON format ONLY:
    {{
        "title": "Optimized Title Here",
        "slug": "optimized-url-slug-contain-keywords",
        "excerpt": "SEO Meta Description (Max 160 chars) - Must be click-worthy.",
        "content_html": "<div>...full html content...</div>",
        "tags": ["Tag1", "Tag2", "SEO Keyword"]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model=AI_MODEL_NAME, 
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        content = content.strip()
        content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
        
        data = json.loads(content)
        
        # Handle Image Fallback
        final_image = news_item.get('image_url')
        if not final_image:
            final_image = get_fallback_image(data['title'], data['tags'])
            
        # Inject Image into HTML if bot didn't (or replace placeholder)
        if 'PLACEHOLDER' in data['content_html']:
             data['content_html'] = data['content_html'].replace('PLACEHOLDER', final_image)
        
        # Make sure we have the cover image field for the JSON listing
        data['cover_image'] = final_image
        
        return data
        
    except Exception as e:
        print(f"Generation failed: {e}")
        return None

def save_to_supabase(post_data, source_link):
    if not supabase: return
    
    print("Saving to Supabase...")
    db_record = {
        "title": post_data["title"],
        "slug": post_data["slug"],
        "summary": post_data["excerpt"],
        "content": post_data["content_html"],
        "author": "Amz AI Agent",
        "tags": post_data["tags"],
        "status": "published",
        "published_at": datetime.now().isoformat(),
        "cover_image": post_data.get('cover_image', "images/blog_thumbs/default_news.png"),
        "source_url": source_link
    }
    
    try:
        supabase.table("blog_posts").insert(db_record).execute()
        print("Saved to DB.")
    except Exception as e:
        print(f"DB Error (ignored): {e}")

def save_to_json(post_data, source_link):
    print("Saving to local JSON...")
    json_path = "data/blog/posts_en.json"
    
    new_entry = {
        "id": post_data["slug"],
        "slug": post_data["slug"],
        "title": post_data["title"],
        "date": datetime.now().strftime("%Y-%m-%d"), 
        "author": "Amz AI Agent",
        "excerpt": post_data["excerpt"],
        "content": post_data["content_html"],
        "cover_image": post_data.get('cover_image', "images/blog_thumbs/default_news.png"),
        "tags": post_data["tags"],
        "source_link": source_link
    }

    try:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        
        if any(d['slug'] == new_entry['slug'] for d in data):
            print("Duplicate slug detected. Skipping JSON save.")
            return

        data.insert(0, new_entry)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Success: JSON updated.")
        
    except Exception as e:
        print(f"JSON Error: {e}")

def main():
    candidates = fetch_and_filter_candidates()
    
    if not candidates:
        print("No recent news found (last 48 hours). Resting today.")
        return

    best_news = select_best_article(candidates)
    if not best_news:
        return

    blog_post = generate_blog_post(best_news)
    
    if blog_post:
        save_to_supabase(blog_post, best_news['link'])
        save_to_json(blog_post, best_news['link'])

if __name__ == "__main__":
    main()
