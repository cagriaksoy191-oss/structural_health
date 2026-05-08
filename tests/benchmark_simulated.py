import asyncio
import time
import concurrent.futures

# Simulating the sync approach (current)
def sync_io_mock(duration=0.5):
    time.sleep(duration)
    return "Done"

async def current_approach(n=10):
    print(f"Running {n} concurrent requests with CURRENT approach (asyncio.to_thread)...")
    start_time = time.perf_counter()
    tasks = [asyncio.to_thread(sync_io_mock) for _ in range(n)]
    await asyncio.gather(*tasks)
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"Current approach took: {duration:.4f} seconds")
    return duration

# Simulating the async approach (optimized)
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
    n_requests = 20  # Increased to show thread pool limits if any, or just concurrency benefits
    curr_dur = await current_approach(n_requests)
    opt_dur = await optimized_approach(n_requests)

    improvement = (curr_dur - opt_dur) / curr_dur * 100
    print(f"\nSummary for {n_requests} concurrent requests:")
    print(f"Baseline (to_thread): {curr_dur:.4f}s")
    print(f"Optimized (native async): {opt_dur:.4f}s")
    print(f"Improvement: {improvement:.2f}%")
    print("\nNote: In a real world scenario with a default thread pool size (often min(32, cpu_count + 4)), "
          "to_thread might perform similarly for small N, but native async scales much better "
          "and avoids thread context switching and memory overhead.")

if __name__ == "__main__":
    asyncio.run(main())
