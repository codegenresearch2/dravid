import unittest
from unittest.mock import patch, MagicMock
import asyncio
import time
import logging
import xml.etree.ElementTree as ET

from drd.metadata.rate_limit_handler import (
    RateLimiter,
    process_single_file,
    process_files,
    MAX_CONCURRENT_REQUESTS,
    MAX_CALLS_PER_MINUTE,
    RATE_LIMIT_PERIOD
)

class TestRateLimitHandler(unittest.IsolatedAsyncioTestCase):

    async def test_rate_limiter(self):
        limiter = RateLimiter(3, 1)
        acquire_times = []
        for _ in range(5):
            await limiter.acquire()
            acquire_times.append(time.time())

        # Check that the first 3 calls were almost instantaneous
        self.assertLess(acquire_times[2] - acquire_times[0], 0.1)
        # Check that the 4th call was delayed
        self.assertGreater(acquire_times[3] - acquire_times[2], 0.9)
        # Check that the total time is at least 1 second
        self.assertGreater(acquire_times[4] - acquire_times[0], 0.9)

    @patch('drd.metadata.rate_limit_handler.call_dravid_api_with_pagination')
    @patch('drd.metadata.rate_limit_handler.extract_and_parse_xml')
    async def test_process_single_file(self, mock_extract_xml, mock_call_api):
        mock_call_api.return_value = "<response><type>python</type><description>A test file</description><exports>test_function</exports><imports>module1</imports></response>"
        mock_root = ET.fromstring(mock_call_api.return_value)
        mock_extract_xml.return_value = mock_root

        result = await process_single_file("test.py", "print('Hello')", "Test project", {"test.py": "file"})

        self.assertEqual(result, ("test.py", "python", "A test file", "test_function", "module1"))

    @patch('drd.metadata.rate_limit_handler.call_dravid_api_with_pagination')
    async def test_process_single_file_error(self, mock_call_api):
        mock_call_api.side_effect = Exception("API Error")

        result = await process_single_file("test.py", "print('Hello')", "Test project", {"test.py": "file"})

        self.assertEqual(result[1:], ("unknown", "Error: API Error", "", ""))

    @patch('drd.metadata.rate_limit_handler.process_single_file')
    async def test_process_files(self, mock_process_single_file):
        mock_process_single_file.side_effect = [
            ("file1.py", "python", "File 1", "func1", "module1"),
            ("file2.py", "python", "File 2", "func2", "module2")
        ]

        files = [("file1.py", "content1"), ("file2.py", "content2")]
        project_context = "Test project"
        folder_structure = {"file1.py": "file", "file2.py": "file"}

        results = await process_files(files, project_context, folder_structure)

        self.assertEqual(results, [
            ("file1.py", "python", "File 1", "func1", "module1"),
            ("file2.py", "python", "File 2", "func2", "module2")
        ])

    @patch('drd.metadata.rate_limit_handler.process_single_file')
    async def test_process_files_concurrency(self, mock_process_single_file):
        async def slow_process(*args):
            await asyncio.sleep(0.1)
            return ("file.py", "python", "Slow file", "func", "module")

        mock_process_single_file.side_effect = slow_process

        files = [("file.py", "content")] * 20  # 20 files
        project_context = "Test project"
        folder_structure = {"file.py": "file"}

        start_time = time.time()
        await process_files(files, project_context, folder_structure)
        end_time = time.time()

        # With MAX_CONCURRENT_REQUESTS = 10, it should take about 0.2 seconds
        self.assertLess(end_time - start_time, 0.3)