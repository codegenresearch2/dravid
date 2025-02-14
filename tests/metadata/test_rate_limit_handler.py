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
        acquire_times = [time.time()]
        for _ in range(5):
            await limiter.acquire()
            acquire_times.append(time.time())

        self.assertLess(acquire_times[2] - acquire_times[0], 0.1)
        self.assertGreater(acquire_times[3] - acquire_times[2], 0.9)
        self.assertGreater(acquire_times[-1] - acquire_times[0], 0.9)

    @patch('drd.metadata.rate_limit_handler.call_dravid_api_with_pagination')
    @patch('drd.metadata.rate_limit_handler.extract_and_parse_xml')
    async def test_process_single_file(self, mock_extract_xml, mock_call_api):
        mock_call_api.return_value = "<response><type>python</type><summary>A test file</summary><exports>test_function</exports><imports>os</imports></response>"
        mock_root = ET.fromstring(mock_call_api.return_value)
        mock_extract_xml.return_value = mock_root

        result = await process_single_file("test.py", "print('Hello')", "Test project", {"test.py": "file"})

        self.assertEqual(result, ("test.py", "python", "A test file", "test_function", "os"))

    @patch('drd.metadata.rate_limit_handler.call_dravid_api_with_pagination')
    async def test_process_single_file_error(self, mock_call_api):
        mock_call_api.side_effect = Exception("API Error")

        result = await process_single_file("test.py", "print('Hello')", "Test project", {"test.py": "file"})

        self.assertEqual(result[0], "test.py")
        self.assertEqual(result[1], "unknown")
        self.assertTrue(result[2].startswith("Error:"))
        self.assertEqual(result[3], "")
        self.assertEqual(result[4], "")

    @patch('drd.metadata.rate_limit_handler.process_single_file')
    async def test_process_files(self, mock_process_single_file):
        mock_process_single_file.side_effect = [
            ("file1.py", "python", "File 1", "func1", "os"),
            ("file2.py", "python", "File 2", "func2", "sys")
        ]

        files = [("file1.py", "content1"), ("file2.py", "content2")]
        project_context = "Test project"
        folder_structure = {"file1.py": "file", "file2.py": "file"}

        results = await process_files(files, project_context, folder_structure)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], ("file1.py", "python", "File 1", "func1", "os"))
        self.assertEqual(results[1], ("file2.py", "python", "File 2", "func2", "sys"))

    @patch('drd.metadata.rate_limit_handler.process_single_file')
    async def test_process_files_concurrency(self, mock_process_single_file):
        async def slow_process(*args):
            await asyncio.sleep(0.1)
            return ("file.py", "python", "Slow file", "func", "time")

        mock_process_single_file.side_effect = slow_process

        files = [("file.py", "content")] * 20
        project_context = "Test project"
        folder_structure = {"file.py": "file"}

        start_time = time.time()
        await process_files(files, project_context, folder_structure)
        end_time = time.time()

        self.assertLess(end_time - start_time, 0.3)