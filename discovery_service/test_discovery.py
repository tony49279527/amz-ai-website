"""
Test script for Product Discovery Service
Run this to test the service without starting the full API
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discovery_service.models import DiscoveryRequest, UserTier, MarketplaceEnum
from discovery_service.analyzer import ProductDiscoveryAnalyzer


async def test_discovery():
    """Test the discovery analyzer"""
    
    print("=" * 60)
    print("Product Discovery Service - Test Run")
    print("=" * 60)
    
    # Create test request
    request = DiscoveryRequest(
        category="Kitchen & Dining",
        keywords="coffee maker",
        marketplace=MarketplaceEnum.US,
        reference_asins=["B08CVS825S"],  # Example ASIN
        user_name="Test User",
        user_email="test@example.com",
        user_industry="E-commerce",
        user_tier=UserTier.FREE
    )
    
    # Run analysis
    analyzer = ProductDiscoveryAnalyzer()
    
    try:
        report = await analyzer.analyze(request)
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"\nReport ID: {report.report_id}")
        print(f"Generated at: {report.generated_at}")
        print(f"Model used: {report.model_used}")
        print(f"Sources analyzed: {report.sources_count}")
        print(f"ASINs analyzed: {report.asins_analyzed}")
        
        print("\n" + "-" * 60)
        print("REPORT PREVIEW (first 1000 characters):")
        print("-" * 60)
        print(report.report_markdown[:1000])
        print("\n... (truncated)")
        
        # Save full report to file
        output_file = f"test_report_{report.report_id[:8]}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report.report_markdown)
        
        print(f"\n✅ Full report saved to: {output_file}")
        
        return report
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_scrapers_only():
    """Test just the scraping functionality"""
    from discovery_service.scrapers import ScrapingBeeClient, AmazonClient
    
    print("\n" + "=" * 60)
    print("Testing Scrapers Only")
    print("=" * 60)
    
    # Test ScrapingBee
    print("\n[1] Testing ScrapingBee...")
    scraper = ScrapingBeeClient()
    
    test_url = "https://www.reddit.com/r/Coffee/top/?t=week"
    print(f"Scraping: {test_url}")
    
    source = await scraper.scrape_reddit_post(test_url)
    if source:
        print(f"✅ Success! Title: {source.title}")
        print(f"Content length: {len(source.content)} chars")
    else:
        print("❌ Failed to scrape")
    
    # Test Amazon API
    print("\n[2] Testing Amazon API...")
    amazon = AmazonClient()
    
    test_asin = "B08CVS825S"
    print(f"Fetching ASIN: {test_asin}")
    
    product = await amazon.get_product_details(test_asin)
    if product:
        print(f"✅ Success! Product: {product.title}")
        print(f"Price: {product.price}")
        print(f"Rating: {product.rating}")
    else:
        print("❌ Failed to fetch product")


async def test_ai_only():
    """Test just the AI generation"""
    from discovery_service.ai import OpenRouterClient
    
    print("\n" + "=" * 60)
    print("Testing AI Client Only")
    print("=" * 60)
    
    client = OpenRouterClient()
    
    test_prompt = "Write a 2-sentence summary of what makes a good coffee maker."
    print(f"\nPrompt: {test_prompt}")
    print("\nGenerating...")
    
    response = await client.generate_with_retry(
        test_prompt,
        model="openai/gpt-4o-mini"
    )
    
    if response:
        print(f"\n[SUCCESS] Response:\n{response}")
    else:
        print("\n[FAILED] Failed to generate")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Product Discovery Service")
    parser.add_argument(
        "--mode",
        choices=["full", "scrapers", "ai"],
        default="full",
        help="Test mode: full analysis, scrapers only, or AI only"
    )
    
    args = parser.parse_args()
    
    if args.mode == "full":
        asyncio.run(test_discovery())
    elif args.mode == "scrapers":
        asyncio.run(test_scrapers_only())
    elif args.mode == "ai":
        asyncio.run(test_ai_only())
