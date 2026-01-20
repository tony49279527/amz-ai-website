import os
import re

BASE_URL = "https://amzflowagent.com"

def fix_seo():
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    for filename in html_files:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        modified = False
        
        # 1. Inject Canonical if missing
        if '<link rel="canonical"' not in content:
            canonical_tag = f'    <link rel="canonical" href="{BASE_URL}/{filename}">\n'
            # Insert before </head>
            if '</head>' in content:
                content = content.replace('</head>', f'{canonical_tag}</head>')
                modified = True
                print(f"Fixed Canonical: {filename}")
        
        # 2. Inject Description if missing (Generic fallback, ideally manual)
        if '<meta name="description"' not in content:
            # Use title as base for description if possible, or generic
            desc_content = "AI-powered Amazon competitor analysis tool. Generate professional reports and gain marketing insights."
            meta_tag = f'    <meta name="description" content="{desc_content}">\n'
            # Insert after <title>
            if '</title>' in content:
                content = content.replace('</title>', f'</title>\n{meta_tag}')
                modified = True
                print(f"Fixed Description: {filename}")

        if modified:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

if __name__ == "__main__":
    fix_seo()
