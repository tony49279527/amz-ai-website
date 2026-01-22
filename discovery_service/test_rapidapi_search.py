
import asyncio
import os
import json
from dotenv import load_dotenv
import httpx

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "35d443d327msh77164428609687ep1ee4b4jsn763b388ea69a")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "real-time-amazon-data.p.rapidapi.com")

async def search_products():
    keywords = "Smart Pet Water Fountain"
    url = f"https://{RAPIDAPI_HOST}/search"
    querystring = {"query": keywords, "page": "1", "country": "US", "sort_by": "RELEVANCE", "category_id": "aps"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    print(f"Searching Amazon for: {keywords}...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=querystring)
            if response.status_code == 200:
                data = response.json()
                products = data.get("data", {}).get("products", [])
                print(f"Found {len(products)} products.")
                
                valid_asins = []
                for p in products[:5]:
                    asin = p.get("asin")
                    title = p.get("product_title")
                    print(f"- {asin}: {title[:50]}...")
                    valid_asins.append(asin)
                
                return valid_asins
            else:
                print("Error:", response.text)
                return []
        except Exception as e:
            print("Exception:", e)
            return []

if __name__ == "__main__":
    asyncio.run(search_products())
