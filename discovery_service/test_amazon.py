"""
Quick test for Amazon API
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discovery_service.scrapers import AmazonClient


async def test_amazon_api():
    """Test Amazon API with a real ASIN"""
    
    print("=" * 60)
    print("Testing Amazon API (Real-Time Amazon Data)")
    print("=" * 60)
    
    client = AmazonClient()
    
    # Test with a popular coffee maker ASIN
    test_asin = "B08CVS825S"
    
    print(f"\n[1/2] Fetching product details for ASIN: {test_asin}")
    product = await client.get_product_details(test_asin, "US")
    
    if product:
        print(f"\n[SUCCESS] Product Details:")
        print(f"  Title: {product.title[:80]}...")
        print(f"  Price: {product.price}")
        print(f"  Rating: {product.rating}")
        print(f"  Reviews: {product.review_count}")
        print(f"  Features: {len(product.features or [])} bullet points")
    else:
        print("\n[FAILED] Could not fetch product details")
        return False
    
    print(f"\n[2/2] Fetching product reviews...")
    reviews = await client.get_product_reviews(test_asin, "US", max_reviews=5)
    
    if reviews:
        print(f"\n[SUCCESS] Fetched {len(reviews)} reviews")
        print("\nSample review:")
        if reviews:
            r = reviews[0]
            print(f"  Rating: {r.get('rating')} stars")
            print(f"  Title: {r.get('title')}")
            print(f"  Text: {r.get('text', '')[:100]}...")
    else:
        print("\n[WARNING] No reviews fetched (might be API limit)")
    
    print("\n" + "=" * 60)
    print("[RESULT] Amazon API test completed successfully!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_amazon_api())
    sys.exit(0 if success else 1)
