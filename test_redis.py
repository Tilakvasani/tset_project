
import redis.asyncio as aioredis
import asyncio

async def test_redis():
    url = "redis://localhost:6379"
    print(f"Connecting to {url}...")
    try:
        client = aioredis.from_url(url, encoding="utf-8", decode_responses=True, socket_connect_timeout=2)
        await client.ping()
        print("✅ Ping successful!")
        await client.aclose()
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_redis())
