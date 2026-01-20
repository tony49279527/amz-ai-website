import os
import re

def validate_seo():
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    report = []
    
    for filename in html_files:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        issues = []
        
        # Check Title
        if not re.search(r'<title>.*?</title>', content, re.IGNORECASE | re.DOTALL):
            issues.append("Missing <title>")
        
        # Check Description
        if not re.search(r'<meta name="description"', content, re.IGNORECASE):
            issues.append("Missing meta description")
            
        # Check Canonical
        if not re.search(r'<link rel="canonical"', content, re.IGNORECASE):
            issues.append("Missing canonical link")
        elif '_en.html' in content: # Double check no leftover _en refs
             if re.search(r'href="[^"]*_en\.html"', content):
                issues.append("Contains link to _en.html (cleanup needed)")

        # Check H1
        if not re.search(r'<h1', content, re.IGNORECASE):
            issues.append("Missing <h1> tag")
            
        if issues:
            report.append(f"❌ {filename}: {', '.join(issues)}")
        else:
            report.append(f"✅ {filename}: SEO checks passed")
            
    print("\nSEO VALIDATION REPORT")
    print("=====================")
    for line in report:
        print(line)

if __name__ == "__main__":
    validate_seo()
