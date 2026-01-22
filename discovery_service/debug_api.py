"""
Debug Amazon API response structure
"""
import asyncio
import httpx
import json

RAPIDAPI_KEY = "35d443d327msh77164428609687ep1ee4b4jsn763b388ea69a"
RAPIDAPI_HOST = "real-time-amazon-data.p.rapidapi.com"


async def debug_api():
    """Check actual API response"""
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    # Test Product Details - try a very popular product
    print("Testing Product Details endpoint...")
    url = f"https://{RAPIDAPI_HOST}/product-details"
    
    # Try multiple ASINs
    test_asins = [
        "B0BSHF69X1",  # Kindle Paperwhite (2023)
        "B09SWV3BYH",  # Echo Dot 5th Gen
        "B0D1XD1ZV3"   # Amazon Fire TV Stick
    ]
    
    for asin in test_asins:
        print(f"\nTrying ASIN: {asin}")
        params = {"asin": asin, "country": "US"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            data = response.json()
            print(f"Status: {response.status_code}")
            
            if data.get("data"):
                print(f"SUCCESS! Got data:")
                print(json.dumps(data, indent=2)[:500])
                break
            else:
                print(f"Empty data for {asin}")


if __name__ == "__main__":
    asyncio.run(debug_api())
