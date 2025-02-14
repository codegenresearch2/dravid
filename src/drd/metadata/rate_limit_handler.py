import functools
import sys
import asyncio
import time
from ..api.main import call_dravid_api_with_pagination
from ..utils.parser import extract_and_parse_xml
from ..prompts.file_metada_desc_prompts import get_file_metadata_prompt
from ..utils.utils import print_info, print_error, print_success, print_warning
from .common_utils import generate_file_description, find_file_with_dravid

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

async def process_single_file(filename, project_context, folder_structure):
    try:
        found_filename = find_file_with_dravid(filename, project_context, folder_structure)
        if not found_filename:
            print_warning(f"Could not find file: {filename}")
            return None

        with open(found_filename, 'r') as file:
            content = file.read()

        file_type, summary, exports = generate_file_description(found_filename, content, project_context, folder_structure)

        return {
            'path': found_filename,
            'type': file_type,
            'summary': summary,
            'exports': exports
        }
    except Exception as e:
        print_error(f"Error processing {filename}: {str(e)}")
        return None

async def process_files(files, project_context, folder_structure):
    total_files = len(files)
    print_info(f"Processing {total_files} files to construct metadata per file")
    print_info(f"LLM calls to be made: {total_files}")

    async def process_batch(batch):
        tasks = [process_single_file(filename, project_context, folder_structure) for filename in batch]
        return await asyncio.gather(*tasks)

    batch_size = MAX_CONCURRENT_REQUESTS
    results = []
    for i in range(0, total_files, batch_size):
        batch = files[i:i+batch_size]
        batch_results = await process_batch(batch)
        results.extend([result for result in batch_results if result is not None])
        print_info(f"Progress: {len(results)}/{total_files} files processed")

    return results