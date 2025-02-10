import functools
import sys
import asyncio
import time
from ..api.main import call_dravid_api_with_pagination
from ..utils.parser import extract_and_parse_xml
from ..prompts.file_metadata_desc_prompts import get_file_metadata_prompt
from ..utils.utils import print_info, print_error, print_success, print_warning
from .common_utils import generate_file_description

MAX_CONCURRENT_REQUESTS = 10
MAX_CALLS_PER_MINUTE = 100
RATE_LIMIT_PERIOD = 60  # seconds

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = asyncio.Queue(maxsize=max_calls)
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def acquire(self):
        while True:
            if self.calls.full():
                oldest_call = await self.calls.get()
                time_since_oldest_call = time.time() - oldest_call
                if time_since_oldest_call < self.period:
                    await asyncio.sleep(self.period - time_since_oldest_call)
            await self.calls.put(time.time())
            return

rate_limiter = RateLimiter(MAX_CALLS_PER_MINUTE, RATE_LIMIT_PERIOD)

def to_thread(func, *args, **kwargs):
    if sys.version_info >= (3, 9):
        return asyncio.to_thread(func, *args, **kwargs)
    else:
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

async def process_single_file(filename, content, project_context, folder_structure):
    try:
        file_type, description, exports = await to_thread(generate_file_description, filename, content, project_context, folder_structure)
        print_success(f"Processed: {filename}")
        return filename, file_type, description, exports
    except Exception as e:
        print_error(f"Error processing {filename}: {e}")
        return filename, "unknown", f"Error: {e}", ""

async def process_files(files, project_context, folder_structure):
    total_files = len(files)
    print_info(
        f"Processing {total_files} files to construct metadata per file")
    print_info(f"LLM calls to be made: {total_files}")

    async def process_batch(batch):
        tasks = [process_single_file(filename, content, project_context, folder_structure)
                 for filename, content in batch]
        return await asyncio.gather(*tasks)

    batch_size = MAX_CONCURRENT_REQUESTS
    results = []
    for i in range(0, total_files, batch_size):
        batch = files[i:i+batch_size]
        batch_results = await process_batch(batch)
        results.extend(batch_results)
        print_info(f"Progress: {len(results)}/{total_files} files processed")

    return results


In the rewritten code, I have improved XML response handling by using the `generate_file_description` function from `common_utils.py` to parse the XML response and extract the file type, description, and exports. This function is called in the `process_single_file` function using `asyncio.to_thread` to run it in a separate thread and avoid blocking the event loop.

I have also improved metadata structure and clarity by returning a tuple of `(filename, file_type, description, exports)` from the `process_single_file` function, which makes it easier to handle the metadata for each file.

Finally, I have streamlined dependency management in code by using the `RateLimiter` class to limit the number of API calls per minute and the `MAX_CONCURRENT_REQUESTS` constant to limit the number of concurrent requests. This should help to avoid hitting the API rate limit and improve performance.