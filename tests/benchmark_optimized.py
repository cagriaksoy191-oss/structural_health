import asyncio
import time

# Optimized approach (native async) - using native async call
async def async_io_mock(duration=0.5):
    await asyncio.sleep(duration)
    return "Done"

async def optimized_approach(n=10):
    print(f"Running {n} concurrent requests with OPTIMIZED approach (native async)...")
    start_time = time.perf_counter()
    tasks = [async_io_mock() for _ in range(n)]
    await asyncio.gather(*tasks)
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"Optimized approach took: {duration:.4f} seconds")
    return duration

async def main():
    n_requests = 20
    await optimized_approach(n_requests)

if __name__ == "__main__":
    asyncio.run(main())
