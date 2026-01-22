"""
Complete end-to-end test with a working ASIN
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discovery_service.models import DiscoveryRequest, UserTier, MarketplaceEnum
from discovery_service.analyzer import ProductDiscoveryAnalyzer


async def test_full_discovery():
    """Test complete discovery workflow"""
    
    print("=" * 70)
    print("PRODUCT DISCOVERY - FULL END-TO-END TEST")
    print("=" * 70)
    
    # Create test request with a working ASIN
    request = DiscoveryRequest(
        category="Electronics",
        keywords="smart speaker",
        marketplace=MarketplaceEnum.US,
        reference_asins=["B09SWV3BYH"],  # Echo Dot 5th Gen (confirmed working)
        user_name="Test User",
        user_email="test@example.com",
        user_industry="E-commerce",
        user_tier=UserTier.FREE  # Use free tier (GPT-4o) for faster testing
    )
    
    print(f"\nTest Parameters:")
    print(f"  Category: {request.category}")
    print(f"  Keywords: {request.keywords}")
    print(f"  Marketplace: {request.marketplace.value}")
    print(f"  Reference ASIN: {request.reference_asins[0]}")
    print(f"  User Tier: {request.user_tier.value}")
    print("\n" + "=" * 70)
    
    # Run analysis
    analyzer = ProductDiscoveryAnalyzer()
    
    try:
        report = await analyzer.analyze(request)
        
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"\nReport ID: {report.report_id}")
        print(f"Generated at: {report.generated_at}")
        print(f"Model used: {report.model_used}")
        print(f"Sources analyzed: {report.sources_count}")
        print(f"ASINs analyzed: {report.asins_analyzed}")
        
        print("\n" + "-" * 70)
        print("REPORT PREVIEW (first 2000 characters):")
        print("-" * 70)
        print(report.report_markdown[:2000])
        print("\n... (report continues)")
        
        # Save full report to file
        output_file = f"full_report_{report.report_id[:8]}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report.report_markdown)
        
        print(f"\n[SUCCESS] Full report saved to: {output_file}")
        print("\n" + "=" * 70)
        
        return report
        
    except Exception as e:
        print(f"\n[FAILED] Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\nThis will take 5-10 minutes to complete...")
    print("Press Ctrl+C to cancel\n")
    
    success = asyncio.run(test_full_discovery())
    sys.exit(0 if success else 1)
