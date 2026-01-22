"""
Real test for Buffing Wheel product discovery
Saves all intermediate data for review
"""
import asyncio
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discovery_service.models import DiscoveryRequest, UserTier, MarketplaceEnum
from discovery_service.analyzer import ProductDiscoveryAnalyzer


async def test_buffing_wheel():
    """Real test with buffing wheel product"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"buffing_wheel_test_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("PRODUCT DISCOVERY - BUFFING WHEEL TEST")
    print("=" * 80)
    
    # Create real request
    request = DiscoveryRequest(
        category="Buffing Wheels",
        keywords="buffing wheel",
        marketplace=MarketplaceEnum.US,
        reference_asins=["B0DJ4Z4RDL", "B0BM6YWTS1", "B0C1RSH46Z"],
        user_name="Tony",
        user_email="leetony4927@gmail.com",
        user_industry="E-commerce",
        user_tier=UserTier.PRO  # Use Pro tier for better quality
    )
    
    print(f"\nTest Parameters:")
    print(f"  Category: {request.category}")
    print(f"  Keywords: {request.keywords}")
    print(f"  Marketplace: {request.marketplace.value}")
    print(f"  Reference ASINs: {', '.join(request.reference_asins)}")
    print(f"  User Email: {request.user_email}")
    print(f"  User Tier: {request.user_tier.value}")
    print(f"\nOutput Directory: {output_dir}")
    print("\n" + "=" * 80)
    
    # Create analyzer
    analyzer = ProductDiscoveryAnalyzer()
    
    # Step 1: Find sources
    print("\n[STEP 1/4] Finding research sources...")
    source_urls = await analyzer.find_research_sources(
        request.category,
        request.keywords,
        request.marketplace.value
    )
    
    # Save source URLs
    with open(f"{output_dir}/01_source_urls.json", "w", encoding="utf-8") as f:
        json.dump({"urls": source_urls, "count": len(source_urls)}, f, indent=2)
    
    print(f"Found {len(source_urls)} sources:")
    for i, url in enumerate(source_urls, 1):
        print(f"  {i}. {url}")
    
    # Step 2: Scrape web sources
    print(f"\n[STEP 2/4] Scraping {len(source_urls)} web sources...")
    web_sources = await analyzer.scrape_web_sources(source_urls)
    
    # Save web sources
    web_sources_data = []
    for i, source in enumerate(web_sources, 1):
        source_data = {
            "index": i,
            "url": source.url,
            "title": source.title,
            "type": source.source_type,
            "content_length": len(source.content),
            "content_preview": source.content[:500]
        }
        web_sources_data.append(source_data)
        
        # Save full content to separate file
        with open(f"{output_dir}/02_source_{i}_{source.source_type}.txt", "w", encoding="utf-8") as f:
            f.write(f"URL: {source.url}\n")
            f.write(f"Title: {source.title}\n")
            f.write(f"Type: {source.source_type}\n")
            f.write(f"\n{'='*80}\n\n")
            f.write(source.content)
    
    with open(f"{output_dir}/02_web_sources_summary.json", "w", encoding="utf-8") as f:
        json.dump(web_sources_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully scraped {len(web_sources)} sources")
    
    # Step 3: Fetch Amazon data
    print(f"\n[STEP 3/4] Fetching Amazon data for {len(request.reference_asins)} ASINs...")
    amazon_products = await analyzer.fetch_amazon_data(
        request.reference_asins,
        request.marketplace.value
    )
    
    # Save Amazon data
    amazon_data = []
    for i, product in enumerate(amazon_products, 1):
        product_data = {
            "index": i,
            "asin": product.asin,
            "title": product.title,
            "price": product.price,
            "rating": product.rating,
            "review_count": product.review_count,
            "features": product.features,
            "reviews_count": len(product.reviews or []),
            "sample_reviews": (product.reviews or [])[:3]
        }
        amazon_data.append(product_data)
    
    with open(f"{output_dir}/03_amazon_products.json", "w", encoding="utf-8") as f:
        json.dump(amazon_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully fetched {len(amazon_products)} products")
    for product in amazon_products:
        print(f"  - {product.asin}: {product.title[:60]}...")
    
    # Step 4: Generate report
    print(f"\n[STEP 4/4] Generating analysis report with Claude Sonnet 3.5...")
    report_markdown = await analyzer.generate_report(
        request.category,
        request.keywords,
        request.marketplace.value,
        web_sources,
        amazon_products,
        model="anthropic/claude-3.5-sonnet"
    )
    
    # Save report
    with open(f"{output_dir}/04_final_report.md", "w", encoding="utf-8") as f:
        f.write(report_markdown)
    
    # Convert to HTML
    import markdown
    report_html = markdown.markdown(report_markdown, extensions=['tables', 'fenced_code'])
    
    with open(f"{output_dir}/04_final_report.html", "w", encoding="utf-8") as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Buffing Wheel Product Discovery Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #2563eb; }}
        h2 {{ color: #1e40af; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
        h3 {{ color: #374151; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f3f4f6; }}
        blockquote {{ background: #f9fafb; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0; }}
        code {{ background: #f3f4f6; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
{report_html}
</body>
</html>
        """)
    
    # Create summary document
    summary = f"""
# BUFFING WHEEL PRODUCT DISCOVERY - DATA SUMMARY
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Test Parameters
- Category: {request.category}
- Keywords: {request.keywords}
- Marketplace: {request.marketplace.value}
- Reference ASINs: {', '.join(request.reference_asins)}
- User Email: {request.user_email}
- Model Used: Claude Sonnet 3.5

## Data Collection Summary

### 1. Web Sources ({len(web_sources)} sources)
{chr(10).join([f"- [{s.source_type}] {s.title[:60]}... ({len(s.content)} chars)" for s in web_sources])}

### 2. Amazon Products ({len(amazon_products)} products)
{chr(10).join([f"- {p.asin}: {p.title[:60]}... (Rating: {p.rating}, Reviews: {p.review_count})" for p in amazon_products])}

### 3. Report Statistics
- Total characters: {len(report_markdown)}
- Estimated reading time: {len(report_markdown) // 1000} minutes

## Files Generated
1. 01_source_urls.json - List of URLs found by AI
2. 02_source_N_TYPE.txt - Full content of each scraped source
3. 02_web_sources_summary.json - Summary of all web sources
4. 03_amazon_products.json - Amazon product data with reviews
5. 04_final_report.md - Final analysis report (Markdown)
6. 04_final_report.html - Final analysis report (HTML)
7. 00_summary.txt - This summary file

## Next Steps
1. Review the final report: 04_final_report.html
2. Check intermediate data in JSON files
3. Copy report to Google Docs: https://docs.google.com/document/d/1tS_iXPhPVOrYLund4yZ-gOzgFeDCjv9XkVoDa5_umGI/edit?tab=t.0

---
All data saved to: {output_dir}/
"""
    
    with open(f"{output_dir}/00_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"\nAll data saved to: {output_dir}/")
    print("\nGenerated files:")
    print("  - 00_summary.txt (Overview)")
    print("  - 01_source_urls.json (AI-found URLs)")
    print(f"  - 02_source_*.txt ({len(web_sources)} scraped sources)")
    print("  - 02_web_sources_summary.json (Source summary)")
    print("  - 03_amazon_products.json (Amazon data)")
    print("  - 04_final_report.md (Markdown report)")
    print("  - 04_final_report.html (HTML report)")
    
    print(f"\n[SUCCESS] Report preview (first 1500 chars):")
    print("-" * 80)
    print(report_markdown[:1500])
    print("\n... (full report in files)")
    print("=" * 80)
    
    return output_dir


if __name__ == "__main__":
    print("\nStarting real buffing wheel analysis...")
    print("This will take 5-10 minutes.\n")
    
    output_dir = asyncio.run(test_buffing_wheel())
    
    print(f"\n\n{'='*80}")
    print("TO VIEW RESULTS:")
    print(f"{'='*80}")
    print(f"1. Open: {output_dir}/04_final_report.html")
    print(f"2. Review data: {output_dir}/00_summary.txt")
    print(f"3. Copy to Google Docs: https://docs.google.com/document/d/1tS_iXPhPVOrYLund4yZ-gOzgFeDCjv9XkVoDa5_umGI/edit?tab=t.0")
    print(f"{'='*80}\n")
