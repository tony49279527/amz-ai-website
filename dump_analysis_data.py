
import asyncio
import os
import json
from dotenv import load_dotenv
from discovery_service.analyzer import ProductDiscoveryAnalyzer
from discovery_service.models import DiscoveryRequest, UserTier

load_dotenv()

async def dump_data():
    analyzer = ProductDiscoveryAnalyzer()
    category = "Pet Supplies"
    keywords = "Smart Pet Water Fountain"
    marketplace = "US"
    asins = ["B07SBXDMZI", "B07HFKJKG8", "B0146QXOB0"]

    print(f"=== REPRODUCING DATA GATHERING FOR: {keywords} ===")
    
    # 1. Web Sources
    print("\n[1] Finding Web Sources (DuckDuckGo)...")
    search_results = await analyzer.find_research_sources(category, keywords, marketplace)
    web_sources = await analyzer.scrape_web_sources(search_results)
    
    # 2. Amazon Data
    print("\n[2] Fetching Amazon Data...")
    amazon_products = await analyzer.fetch_amazon_data(asins, marketplace)

    # 3. Dump to File
    output_file = "analysis_data_dump.md"
    with open(output_file, "w") as f:
        f.write(f"# RAW ANALYSIS DATA: {keywords}\n\n")
        
        f.write("## 1. WEB SOURCES (DuckDuckGo + Fallback)\n")
        if not web_sources:
             f.write("(No web sources found - this should not happen with fallback)\n")
        
        for i, source in enumerate(web_sources):
            f.write(f"### Source {i+1}: {source.title}\n")
            f.write(f"- **URL**: {source.url}\n")
            f.write(f"- **Type**: {source.source_type}\n")
            f.write(f"- **Content Length**: {len(source.content)} chars\n")
            f.write("#### Content Snippet:\n")
            f.write(f"```text\n{source.content}\n```\n\n")
            
        f.write("\n---\n\n")
        f.write("## 2. AMAZON PRODUCT DATA (RapidAPI)\n")
        for i, prod in enumerate(amazon_products):
            f.write(f"### Product {i+1}: {prod.title}\n")
            f.write(f"- **ASIN**: {prod.asin}\n")
            f.write(f"- **Price**: {prod.price}\n")
            f.write(f"- **Rating**: {prod.rating} ({prod.review_count} reviews)\n")
            f.write("#### Reviews:\n")
            if prod.reviews:
                for r in prod.reviews:
                    f.write(f"- [{r.get('rating')}★] {r.get('title')}: {r.get('text')}\n")
            else:
                f.write("(No reviews fetched for this ASIN)\n")
            f.write("\n")

    print(f"\nData dumped to {output_file}")

if __name__ == "__main__":
    asyncio.run(dump_data())
