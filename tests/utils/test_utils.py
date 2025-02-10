import unittest
import os
import json
from unittest.mock import patch, mock_open
from io import StringIO
from colorama import Fore, Style

from drd.utils.utils import (
    print_error,
    print_success,
    print_info,
    print_warning,
    print_debug,
    print_step,
)


class TestUtilityFunctions(unittest.TestCase):

    def setUp(self):
        self.metadata = {
            "project_name": "Test Project",
            "version": "1.0.0"
        }

    @patch('click.echo')
    def test_print_error(self, mock_echo):
        print_error("Test error message")
        mock_echo.assert_called_with(
            f"{Fore.RED}✘ {Style.RESET_ALL}Test error message")

    @patch('click.echo')
    def test_print_success(self, mock_echo):
        print_success("Test success message")
        mock_echo.assert_called_with(
            f"{Fore.GREEN}✔ {Style.RESET_ALL}Test success message")

    @patch('click.echo')
    def test_print_info(self, mock_echo):
        print_info("Test info message")
        mock_echo.assert_called_with(
            f"{Fore.YELLOW}ℹ {Style.RESET_ALL}Test info message")

    @patch('click.echo')
    def test_print_warning(self, mock_echo):
        print_warning("Test warning message")
        mock_echo.assert_called_with(
            f"{Fore.YELLOW}⚠ {Style.RESET_ALL}Test warning message")

    @patch('click.echo')
    @patch('click.style')
    def test_print_debug(self, mock_style, mock_echo):
        print_debug("Test debug message")
        mock_style.assert_called_with("DEBUG: Test debug message", fg="cyan")
        mock_echo.assert_called_once_with(mock_style.return_value)

    @patch('click.echo')
    def test_print_step(self, mock_echo):
        print_step(1, 5, "Test step message")
        mock_echo.assert_called_with(
            f"{Fore.CYAN}[1/5] {Style.RESET_ALL}Test step message")