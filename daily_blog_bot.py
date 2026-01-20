import os
import json
import time
import feedparser
from datetime import datetime
from openai import OpenAI
from supabase import create_client, Client

# ==========================================
# 🔧 用户控制面板 (USER CONTROL PANEL)
# ==========================================

# 1. RSS 订阅列表 (把您的 RSS 链接粘贴在这里)
RSS_FEEDS = [
    "https://www.ecommercebytes.com/feed/", 
    "https://tamebay.com/feed",
    # 在这里添加更多链接，例如: "https://example.com/feed",
]

# 2. 每天发布文章数量限制 (防止发太多)
LIMIT_POSTS_PER_RUN = 1

# 3. AI 模型选择 (OpenRouter 支持的模型)
# 推荐: "anthropic/claude-3.5-sonnet" (质量最好) 或 "openai/gpt-4o"
AI_MODEL_NAME = "anthropic/claude-3.5-sonnet"

# ==========================================
# ⚙️ 系统配置 (System Config) - 勿动
# ==========================================

# Initialize Clients
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # 对应 GitHub Secret: SUPABASE_SERVICE_ROLE_KEY
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY") # 对应 GitHub Secret: OPENROUTER_API_KEY
site_url = "https://amzaiagent.com" # Your site URL for OpenRouter headers

if not all([supabase_url, supabase_key, openrouter_api_key]):
    print("Error: Missing environment variables. Please check GitHub Secrets.")
    # For local test, we might skip exit, but for prod it's fatal
    # exit(1) 

supabase: Client = create_client(supabase_url, supabase_key)

# Configure OpenAI client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
    default_headers={
        "HTTP-Referer": site_url, # Required by OpenRouter for ranking
        "X-Title": "Amz AI Agent Bot", # Optional
    },
)

def fetch_latest_news():
    """Fetches the latest entry from RSS feeds."""
    print("Fetching RSS feeds...")
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            if feed.entries:
                # Return the very first entry we find (simplified logic)
                # In a real app, you might want to check DB to avoid duplicates
                entry = feed.entries[0]
                print(f"Found news: {entry.title}")
                return {
                    "title": entry.title,
                    "link": entry.link,
                    "summary": getattr(entry, 'summary', '') or getattr(entry, 'description', '')
                }
        except Exception as e:
            print(f"Error parsing feed {feed_url}: {e}")
            continue
    return None

def check_if_exists(title):
    try:
        response = supabase.table("blog_posts").select("id").eq("title", title).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"DB Check error: {e}")
        return False

def generate_blog_post(news_item):
    """Uses LLM to write a blog post based on the news."""
    print("Generating content with AI...")
    
    prompt = f"""
    You are an expert Amazon FBA consultant and senior e-commerce analyst.
    Write a blog post for "Amz AI Agent" based on the following news:
    
    News Title: {news_item['title']}
    News Link: {news_item['link']}
    News Summary: {news_item['summary']}
    
    Requirements:
    1. Title: Catchy, SEO-optimized, focusing on impact for Amazon Sellers.
    2. Tone: Professional, insightful, yet accessible. Avoid generic AI fluff.
    3. Structure:
       - What happened? (Brief summary)
       - Why it matters? (Analysis)
       - Actionable advice for sellers.
    4. Format: HTML (use <h2>, <p>, <ul>, <li>, <strong>). Do NOT use <html> or <body> tags.
    5. Length: 600-800 words.
    
    Output JSON format:
    {{
        "title": "The generated title",
        "slug": "the-generated-slug",
        "excerpt": "A short 150-char summary for meta description",
        "content_html": "The full HTML article content",
        "tags": ["tag1", "tag2"]
    }}
    """
    
    response = client.chat.completions.create(
        model=AI_MODEL_NAME, 
        messages=[{"role": "user", "content": prompt}],
        # OpenRouter usually supports json_object, but check specific model capabilities if errors occur
        # Claude 3.5 Sonnet supports tool use or just standard prompting. 
        # For safety with OpenRouter wrapper, we'll ask for JSON in prompt and try to parse.
        # But 'response_format' is standard OpenAI API now.
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content.strip()
    
    # Clean Markdown code blocks if present
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
        
    # Attempt to fix common JSON issues (simple approach)
    content = content.strip()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("Detailed JSON Error. Raw content received:")
        print(content)
        # Fallback: simple text cleanup
        import re
        content_clean = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
        try:
             return json.loads(content_clean)
        except:
            print("Failed to parse JSON even after cleanup.")
            return None

def save_to_supabase(post_data, source_link):
    """Saves the generated post to Supabase."""
    print("Saving to Supabase...")
    
    db_record = {
        "title": post_data["title"],
        "slug": post_data["slug"],
        "summary": post_data["excerpt"],
        "content": post_data["content_html"],
        "author": "AI Analyst",
        "tags": post_data["tags"],
        "status": "published", # Or 'draft' if you want manual review
        "published_at": datetime.now().isoformat(),
        "cover_image": "images/blog_thumbs/default_news.png", # Placeholder
        "source_url": source_link
    }
    
    try:
        supabase.table("blog_posts").insert(db_record).execute()
        print(f"Successfully published: {post_data['title']}")
    except Exception as e:
        print(f"Failed to save to DB: {e}")

def save_to_json(post_data, source_link):
    """Saves the generated post to the local JSON file (data/blog/posts_en.json)."""
    json_path = "data/blog/posts_en.json"
    
    # Create new entry
    new_entry = {
        "id": post_data["slug"], # Use slug as ID for simplicity in new system
        "slug": post_data["slug"],
        "title": post_data["title"],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "author": "AI Analyst",
        "excerpt": post_data["excerpt"],
        "content": post_data["content_html"],
        "cover_image": "images/blog_thumbs/default_news.png",
        "tags": post_data["tags"]
    }

    try:
        # Read existing data
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        
        # Prepend new entry
        data.insert(0, new_entry)
        
        # Write back
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved to JSON: {json_path}")
        
    except Exception as e:
        print(f"Failed to save to JSON: {e}")

def main():
    news = fetch_latest_news()
    if not news:
        print("No news found.")
        return

    if check_if_exists(news['title']): # Simple check using original title
        print("News already processed. Skipping.")
        return

    blog_post = generate_blog_post(news)
    if blog_post:
        # Save to DB (optional now but good for backup)
        save_to_supabase(blog_post, news['link'])
        # Save to JSON (critical for static site)
        save_to_json(blog_post, news['link'])

if __name__ == "__main__":
    main()
