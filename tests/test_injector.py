"""Unit tests for text injection."""

import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from injector import inject_text


class TestInjectText:
    """Test the inject_text function."""

    @patch("injector._keyboard")
    def test_types_text(self, mock_kb):
        inject_text("Hello world")
        mock_kb.type.assert_called_once_with("Hello world")

    @patch("injector._keyboard")
    def test_empty_string_does_nothing(self, mock_kb):
        inject_text("")
        mock_kb.type.assert_not_called()

    @patch("injector._keyboard")
    def test_none_does_nothing(self, mock_kb):
        inject_text(None)
        mock_kb.type.assert_not_called()

    @patch("injector._keyboard")
    def test_strips_newlines(self, mock_kb):
        inject_text("Hello\nworld")
        mock_kb.type.assert_called_once_with("Hello world")

    @patch("injector._keyboard")
    def test_strips_carriage_returns(self, mock_kb):
        inject_text("Hello\r\nworld")
        mock_kb.type.assert_called_once_with("Hello world")

    @patch("injector._keyboard")
    def test_strips_bare_carriage_return(self, mock_kb):
        inject_text("Hello\rworld")
        mock_kb.type.assert_called_once_with("Hello world")

    @patch("injector._keyboard")
    def test_multiple_newlines(self, mock_kb):
        inject_text("Line one\nLine two\nLine three")
        mock_kb.type.assert_called_once_with("Line one Line two Line three")
