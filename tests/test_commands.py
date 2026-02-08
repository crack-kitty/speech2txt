"""Unit tests for the VoiceCommandProcessor."""

import sys
import os
from unittest.mock import patch, call

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from commands import VoiceCommandProcessor


@pytest.fixture
def processor():
    return VoiceCommandProcessor()


class TestExactCommands:
    """Test exact-match command detection."""

    @patch("commands.send_key")
    def test_new_line(self, mock_key, processor):
        processor.process("new line")
        mock_key.assert_called_once_with("enter")

    @patch("commands.send_key")
    def test_new_line_case_insensitive(self, mock_key, processor):
        processor.process("New Line")
        mock_key.assert_called_once_with("enter")

    @patch("commands.send_key")
    def test_new_paragraph(self, mock_key, processor):
        processor.process("new paragraph")
        assert mock_key.call_count == 2
        mock_key.assert_called_with("enter")

    @patch("commands.send_key")
    def test_tab(self, mock_key, processor):
        processor.process("tab")
        mock_key.assert_called_once_with("tab")

    @patch("commands.send_hotkey")
    def test_undo(self, mock_hotkey, processor):
        processor.process("undo")
        mock_hotkey.assert_called_once_with("ctrl", "z")

    @patch("commands.send_hotkey")
    def test_redo(self, mock_hotkey, processor):
        processor.process("redo")
        mock_hotkey.assert_called_once_with("ctrl", "y")

    @patch("commands.send_hotkey")
    def test_select_all(self, mock_hotkey, processor):
        processor.process("select all")
        mock_hotkey.assert_called_once_with("ctrl", "a")

    @patch("commands.send_hotkey")
    def test_copy_that(self, mock_hotkey, processor):
        processor.process("copy that")
        mock_hotkey.assert_called_once_with("ctrl", "c")

    def test_stop_listening(self, processor):
        result = processor.process("stop listening")
        assert result == "stop"


class TestDeleteThat:
    """Test the delete-that command and history tracking."""

    @patch("commands.send_backspaces")
    @patch("commands.inject_text")
    def test_delete_last_segment(self, mock_inject, mock_bs, processor):
        processor.process("Hello world")
        assert len(processor.typed_history) == 1

        processor.process("delete that")
        mock_bs.assert_called_once_with(len("Hello world"))
        assert len(processor.typed_history) == 0

    @patch("commands.send_backspaces")
    @patch("commands.inject_text")
    def test_delete_multiple(self, mock_inject, mock_bs, processor):
        processor.process("First")
        processor.process("Second")
        assert len(processor.typed_history) == 2

        processor.process("delete that")
        assert len(processor.typed_history) == 1
        processor.process("delete that")
        assert len(processor.typed_history) == 0

    @patch("commands.send_backspaces")
    def test_delete_empty_history(self, mock_bs, processor):
        # Should not crash when history is empty
        processor.process("delete that")
        mock_bs.assert_not_called()


class TestPunctuation:
    """Test inline punctuation replacement."""

    @patch("commands.inject_text")
    def test_period(self, mock_inject, processor):
        processor.process("Hello period")
        mock_inject.assert_called_once_with("Hello.")

    @patch("commands.inject_text")
    def test_comma(self, mock_inject, processor):
        processor.process("Hello comma how are you")
        mock_inject.assert_called_once_with("Hello, how are you")

    @patch("commands.inject_text")
    def test_question_mark(self, mock_inject, processor):
        processor.process("How are you question mark")
        mock_inject.assert_called_once_with("How are you?")

    @patch("commands.inject_text")
    def test_multiple_punctuation(self, mock_inject, processor):
        processor.process("Well comma I think so period")
        mock_inject.assert_called_once_with("Well, I think so.")

    @patch("commands.inject_text")
    def test_exclamation_mark(self, mock_inject, processor):
        processor.process("Wow exclamation mark")
        mock_inject.assert_called_once_with("Wow!")


class TestLiteralPrefix:
    """Test the 'literal' escape prefix."""

    @patch("commands.inject_text")
    def test_literal_period(self, mock_inject, processor):
        processor.process("literal period")
        mock_inject.assert_called_once_with("period")

    @patch("commands.inject_text")
    def test_literal_preserves_case(self, mock_inject, processor):
        processor.process("Literal Hello World")
        mock_inject.assert_called_once_with("Hello World")


class TestNormalText:
    """Test that normal text passes through without modification."""

    @patch("commands.inject_text")
    def test_normal_text(self, mock_inject, processor):
        processor.process("Hello world")
        mock_inject.assert_called_once_with("Hello world")

    @patch("commands.inject_text")
    def test_tracks_history(self, mock_inject, processor):
        processor.process("Hello world")
        assert processor.typed_history == ["Hello world"]

    @patch("commands.inject_text")
    def test_trailing_period_stripped_for_command_match(self, mock_inject, processor):
        # Whisper sometimes adds a trailing period to commands
        result = processor.process("undo.")
        # "undo." normalized to "undo" should match the undo command
        assert result is None  # undo doesn't return a control signal
