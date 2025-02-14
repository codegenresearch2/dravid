import functools
import sys
import asyncio
import time
from xml.etree import ElementTree
from ..api.main import call_dravid_api_with_pagination
from ..utils.parser import extract_and_parse_xml
from ..prompts.file_metadata_desc_prompts import get_file_metadata_prompt
from ..utils.utils import print_info, print_error, print_success, print_warning

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

def parse_file_metadata(xml_string):
    root = ElementTree.fromstring(xml_string)
    metadata = root.find('.//metadata')
    if metadata is None:
        raise ValueError("Metadata section not found in the response")

    type_element = metadata.find('type')
    description_element = metadata.find('description')
    exports_element = metadata.find('exports')

    file_type = type_element.text.strip() if type_element is not None and type_element.text else "unknown"
    description = description_element.text.strip() if description_element is not None and description_element.text else "No description available"
    exports = exports_element.text.strip() if exports_element is not None and exports_element.text else ""

    return file_type, description, exports

async def process_single_file(filename, content, project_context, folder_structure):
    metadata_query = get_file_metadata_prompt(filename, content, project_context, folder_structure)
    try:
        async with rate_limiter.semaphore:
            await rate_limiter.acquire()
            response = await to_thread(call_dravid_api_with_pagination, metadata_query, include_context=True)

        file_type, description, exports = parse_file_metadata(response)
        print_success(f"Processed: {filename}")
        return {'path': filename, 'type': file_type, 'description': description, 'exports': exports}
    except Exception as e:
        print_error(f"Error processing {filename}: {e}")
        return {'path': filename, 'type': "unknown", 'description': f"Error: {e}", 'exports': ""}

async def process_files(files, project_context, folder_structure):
    total_files = len(files)
    print_info(f"Processing {total_files} files to construct metadata per file")
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

In the provided code, I have extracted the XML parsing logic for file metadata into a separate function `parse_file_metadata`. This function takes the XML string as input and returns the parsed file type, description, and exports.

This helps improve XML response handling and make the code more modular and easier to understand.

I have also updated the `process_single_file` function to return a dictionary containing the file metadata instead of individual variables. This improves metadata structure and clarity by grouping related information together.

The rate limiter class is maintained as is, ensuring that the API calls are made within the specified rate limit.

The dependency management in the code is streamlined by using asyncio's semaphore for concurrent API calls and asyncio's `to_thread` function to run blocking API calls in a separate thread.

These changes enhance the code according to the provided rules and improve its overall structure and clarity.