
import asyncio
import os
import json
from dotenv import load_dotenv
from discovery_service.analyzer import ProductDiscoveryAnalyzer
from discovery_service.models import DiscoveryRequest, UserTier

load_dotenv()

async def dump_data_v2():
    analyzer = ProductDiscoveryAnalyzer()
    category = "Pet Supplies"
    keywords = "Smart Pet Water Fountain"
    marketplace = "US"
    # The NEW live ASINs found in Step 2253
    asins = ["B0F9FC7JYD", "B0DQ1556BW", "B0G1YB3RRC"]

    print(f"=== REPRODUCING V2 DATA GATHERING FOR: {keywords} ===")
    
    # 1. Web Sources
    print("\n[1] Finding Web Sources (DuckDuckGo 25 Results)...")
    search_results = await analyzer.find_research_sources(category, keywords, marketplace)
    web_sources = await analyzer.scrape_web_sources(search_results)
    
    # 2. Amazon Data
    print("\n[2] Fetching Amazon Data (Fresh ASINs)...")
    amazon_products = await analyzer.fetch_amazon_data(asins, marketplace)

    # 3. Dump to File
    output_file = "analysis_data_dump_v2.md"
    with open(output_file, "w") as f:
        f.write(f"# RAW ANALYSIS DATA V2 (Fresh ASINs): {keywords}\n\n")
        
        f.write("## 1. WEB SOURCES\n")
        f.write(f"(Total Sources: {len(web_sources)})\n")
        for i, source in enumerate(web_sources):
            f.write(f"### Source {i+1}: {source.title}\n")
            f.write(f"- **URL**: {source.url}\n")
            f.write(f"- **Type**: {source.source_type}\n")
            f.write("#### Content Snippet:\n")
            f.write(f"```text\n{source.content[:500]}...\n```\n\n")
            
        f.write("\n---\n\n")
        f.write("## 2. AMAZON PRODUCT DATA (Live ASINs)\n")
        for i, prod in enumerate(amazon_products):
            f.write(f"### Product {i+1}: {prod.title}\n")
            f.write(f"- **ASIN**: {prod.asin}\n")
            f.write(f"- **Price**: {prod.price}\n")
            f.write(f"- **Rating**: {prod.rating} ({prod.review_count} reviews)\n")
            f.write(f"#### Fetched Reviews Count: {len(prod.reviews) if prod.reviews else 0}\n")
            if prod.reviews:
                for r in prod.reviews:
                    rating = r.get('rating')
                    title = r.get('title')
                    text = r.get('text', '')
                    f.write(f"- [{rating}★] **{title}**: {text[:200]}...\n")
            else:
                f.write("(No reviews fetched)\n")
            f.write("\n")

    print(f"\nData dumped to {output_file}")

if __name__ == "__main__":
    asyncio.run(dump_data_v2())
