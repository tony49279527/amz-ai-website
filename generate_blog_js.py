import json
import os

def generate_blog_js():
    base_dir = '/Users/liangxile/.gemini/antigravity/scratch/flowaiagent-replica'
    cn_path = os.path.join(base_dir, 'data/blog/posts.json')
    en_path = os.path.join(base_dir, 'data/blog/posts_en.json')
    output_path = os.path.join(base_dir, 'data/blog/blog_posts.js')

    try:
        with open(cn_path, 'r', encoding='utf-8') as f:
            posts_cn = json.load(f)
        with open(en_path, 'r', encoding='utf-8') as f:
            posts_en = json.load(f)
            
        js_content = f"""
window.blogPostsCN = {json.dumps(posts_cn, indent=2, ensure_ascii=False)};
window.blogPostsEN = {json.dumps(posts_en, indent=2, ensure_ascii=False)};
"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"Generated {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_blog_js()
