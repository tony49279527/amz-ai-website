
import asyncio
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "35d443d327msh77164428609687ep1ee4b4jsn763b388ea69a")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "real-time-amazon-data.p.rapidapi.com")

async def test_rapidapi():
    asin = "B07SBXDMZI" # Veken
    url = f"https://{RAPIDAPI_HOST}/product-details"
    querystring = {"asin": asin, "country": "US"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    print(f"Testing RapidAPI for ASIN: {asin}...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=querystring)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("Success! Title:", data.get("data", {}).get("product_title"))
                print("Reviews count:", data.get("data", {}).get("reviews_count"))
            else:
                print("Error:", response.text)
        except Exception as e:
            print("Exception:", e)

if __name__ == "__main__":
    asyncio.run(test_rapidapi())
