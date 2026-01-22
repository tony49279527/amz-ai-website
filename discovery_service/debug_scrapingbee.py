"""
Debug ScrapingBee API to find the issue
"""
import asyncio
import httpx

SCRAPINGBEE_API_KEY = "FZRSC69J3MPE5OO5FYJKEZFGI2XWG65IQA2V86EFJWKF9ARVGV0AIPMTSJ74XL0FV3EZIL95B7ZQI1XR"


async def debug_scrapingbee():
    """Test ScrapingBee API directly"""
    
    print("=" * 60)
    print("Testing ScrapingBee API")
    print("=" * 60)
    
    # Test with a simple URL first
    test_urls = [
        "https://www.amazon.com/s?k=buffing+wheel",
        "https://www.google.com",
        "https://www.reddit.com"
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url[:50]}...")
        
        params = {
            "api_key": SCRAPINGBEE_API_KEY,
            "url": url,
            "render_js": "false"  # Try without JS first
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    "https://app.scrapingbee.com/api/v1/",
                    params=params
                )
                
                print(f"  Status: {response.status_code}")
                print(f"  Content length: {len(response.text)} chars")
                
                if response.status_code == 200:
                    print(f"  [OK] Success!")
                    print(f"  Preview: {response.text[:200]}...")
                else:
                    print(f"  [FAIL] Error: {response.text[:200]}")
                    
        except Exception as e:
            print(f"  [EXCEPTION] {str(e)}")
    
    # Check API credits
    print("\n" + "=" * 60)
    print("Checking API credits...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://app.scrapingbee.com/api/v1/usage",
                params={"api_key": SCRAPINGBEE_API_KEY}
            )
            print(f"Usage API Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")


if __name__ == "__main__":
    asyncio.run(debug_scrapingbee())
