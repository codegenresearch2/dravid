import unittest
import os
import json
from unittest.mock import patch, mock_open
from io import StringIO
from colorama import Fore, Style

from drd.utils.utils import (
    log_error,
    log_success,
    log_info,
    log_warning,
    log_debug,
    log_step,
)

class TestUtilityFunctions(unittest.TestCase):

    def setUp(self):
        self.metadata = {
            "project_name": "Test Project",
            "version": "1.0.0"
        }

    @patch('click.echo')
    def test_log_error(self, mock_echo):
        log_error("Test error message")
        mock_echo.assert_called_with(
            f"{Fore.RED}✘ Error: Test error message. Please check the context for more details.{Style.RESET_ALL}")

    @patch('click.echo')
    def test_log_success(self, mock_echo):
        log_success("Test success message")
        mock_echo.assert_called_with(
            f"{Fore.GREEN}✔ Success: Test success message{Style.RESET_ALL}")

    @patch('click.echo')
    def test_log_info(self, mock_echo):
        log_info("Test info message")
        mock_echo.assert_called_with(
            f"{Fore.YELLOW}ℹ Info: Test info message{Style.RESET_ALL}")

    @patch('click.echo')
    def test_log_warning(self, mock_echo):
        log_warning("Test warning message")
        mock_echo.assert_called_with(
            f"{Fore.YELLOW}⚠ Warning: Test warning message. Proceed with caution.{Style.RESET_ALL}")

    @patch('click.echo')
    @patch('click.style')
    def test_log_debug(self, mock_style, mock_echo):
        log_debug("Test debug message")
        mock_style.assert_called_with("DEBUG: Test debug message", fg="cyan")
        mock_echo.assert_called_once()

    @patch('click.echo')
    def test_log_step(self, mock_echo):
        log_step(1, 5, "Test step message")
        mock_echo.assert_called_with(
            f"{Fore.CYAN}[1/5] Step: Test step message{Style.RESET_ALL}")