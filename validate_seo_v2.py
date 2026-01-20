import os
import re
from bs4 import BeautifulSoup

def check_seo(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    report = []
    filename = os.path.basename(file_path)
    
    # 1. Title
    title = soup.find('title')
    if not title or not title.string:
        report.append(f"❌ [Title] Missing or empty")
    else:
        if len(title.string) > 60:
            report.append(f"⚠️ [Title] Too long ({len(title.string)} chars): {title.string}")
        else:
            report.append(f"✅ [Title] {title.string}")

    # 2. Meta Description
    desc = soup.find('meta', attrs={'name': 'description'})
    if not desc or not desc.get('content'):
        report.append(f"❌ [Meta Description] Missing or empty")
    else:
        content = desc.get('content')
        if len(content) < 50:
             report.append(f"⚠️ [Meta Description] Too short ({len(content)} chars)")
        elif len(content) > 160:
             report.append(f"⚠️ [Meta Description] Too long ({len(content)} chars)")
        else:
             report.append(f"✅ [Meta Description] Present")

    # 3. Canonical
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if not canonical or not canonical.get('href'):
        report.append(f"❌ [Canonical] Missing")
    else:
        report.append(f"✅ [Canonical] {canonical.get('href')}")

    # 4. H1
    h1s = soup.find_all('h1')
    if len(h1s) == 0:
        report.append(f"❌ [H1] Missing")
    elif len(h1s) > 1:
        report.append(f"❌ [H1] Multiple H1 tags ({len(h1s)}) found")
    else:
        report.append(f"✅ [H1] Present: {h1s[0].get_text(strip=True)[:30]}...")

    # 5. Images Alt
    images = soup.find_all('img')
    missing_alt = [img.get('src', 'unknown') for img in images if not img.get('alt')]
    if missing_alt:
        report.append(f"❌ [Images] {len(missing_alt)} images missing alt text: {missing_alt}")
    else:
        report.append(f"✅ [Images] All {len(images)} images have alt text")

    return filename, report

def main():
    files = [f for f in os.listdir('.') if f.endswith('.html') and f not in ['create_old.html', 'logo_preview.html', 'failed.html', 'success.html']]
    
    print("SEO AUDIT REPORT")
    print("=================")
    for file in files:
        filename, report = check_seo(file)
        print(f"\n📄 {filename}")
        for item in report:
            print(f"  {item}")

if __name__ == "__main__":
    main()
