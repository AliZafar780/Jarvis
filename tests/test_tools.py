"""Tests for the tools system."""

import unittest
from unittest.mock import patch, MagicMock
from jarvis.tools import (
    SystemTools, FileTools, UtilityTools,
    execute_tool, ToolResult
)


class TestSystemTools(unittest.TestCase):
    """Test system tools."""

    def test_get_time(self):
        """Test time tool."""
        result = UtilityTools.get_time()
        self.assertTrue(result.success)
        self.assertIn("202", result.message)  # Year

    def test_calculate(self):
        """Test calculator."""
        result = UtilityTools.calculate("2 + 2")
        self.assertTrue(result.success)
        self.assertEqual(result.data["result"], 4)

    def test_calculate_invalid(self):
        """Test calculator with invalid input."""
        result = UtilityTools.calculate("2 + import os")
        self.assertFalse(result.success)


class TestFileTools(unittest.TestCase):
    """Test file tools."""

    @patch('jarvis.tools.Path')
    def test_list_directory(self, mock_path):
        """Test list directory."""
        # Mock path
        mock_instance = MagicMock()
        mock_instance.exists.return_value = True
        mock_instance.iterdir.return_value = []
        mock_instance.resolve.return_value = mock_instance
        mock_path.return_value = mock_instance

        result = FileTools.list_directory(".")
        self.assertTrue(result.success)


class TestToolRegistry(unittest.TestCase):
    """Test tool registry."""

    def test_execute_unknown_tool(self):
        """Test executing unknown tool."""
        result = execute_tool("unknown_tool")
        self.assertFalse(result.success)
        self.assertIn("Unknown tool", result.message)

    def test_execute_time_tool(self):
        """Test executing time tool through registry."""
        result = execute_tool("time")
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
