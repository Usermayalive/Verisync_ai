import asyncio
import httpx
import time
from backend.config import settings
API_URL = "http://localhost:8000/api/ask"
HEADERS = {"X-API-Key": settings.API_SECRET_KEY}
CONCURRENT_REQUESTS = 10
async def fire_query(client, i):
    start = time.perf_counter()
    try:
        resp = await client.post(API_URL, json={"question": f"Stress test query {i}"}, headers=HEADERS, timeout=60.0)
        end = time.perf_counter()
        return i, resp.status_code, end - start
    except Exception as e:
        return i, "ERROR", str(e)
async def run_stress_test():
    async with httpx.AsyncClient() as client:
        tasks = [fire_query(client, i) for i in range(CONCURRENT_REQUESTS)]
        results = await asyncio.gather(*tasks)
        success_count = sum(1 for _, status, _ in results if status == 200)
        latencies = [lat for _, status, lat in results if isinstance(lat, float)]
        print("\n" + "="*40)
        print("STRESS TEST RESULTS")
        print("="*40)
        print(f"Total Requests: {CONCURRENT_REQUESTS}")
        print(f"Successful: {success_count}")
        if latencies:
            print(f"Avg Latency: {sum(latencies)/len(latencies):.2f}s")
            print(f"Max Latency: {max(latencies):.2f}s")
        print("="*40)
if __name__ == "__main__":
    print("Ensure the FastAPI server is running with 'uvicorn main:app' before this test.")
    asyncio.run(run_stress_test())
