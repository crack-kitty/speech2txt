"""Unit tests for text post-processing in Speech2Txt."""

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from main import Speech2Txt


@pytest.fixture
def app():
    """Create a Speech2Txt instance with mocked dependencies."""
    # Mock everything that touches hardware/GUI
    with (
        pytest.MonkeyPatch.context() as mp,
    ):
        mp.setattr("main.AudioRecorder", MagicMock)
        mp.setattr("main.Transcriber", MagicMock)
        mp.setattr("main.HotkeyListener", MagicMock)
        mp.setattr("main.TrayApp", MagicMock)
        instance = Speech2Txt()
        return instance


class TestSpelledLetters:
    """Test collapsing spelled-out letters like D-I-R or D.I.R."""

    def test_collapse_hyphenated(self, app):
        result = app._post_process("Type D-I-R please")
        assert "dir" in result

    def test_collapse_dotted(self, app):
        result = app._post_process("Run C.M.D. now")
        assert "cmd" in result

    def test_collapse_spaced_dots(self, app):
        result = app._post_process("Try D. I. R. here")
        assert "dir" in result


class TestAllCapsLowering:
    """Test lowercasing short all-caps words that aren't acronyms."""

    def test_lowercase_unknown_caps(self, app):
        result = app._post_process("Type DIR now")
        assert "dir" in result

    def test_preserve_known_acronym_api(self, app):
        result = app._post_process("Use the API")
        assert "API" in result

    def test_preserve_known_acronym_cpu(self, app):
        result = app._post_process("Check CPU usage")
        assert "CPU" in result

    def test_preserve_known_acronym_url(self, app):
        result = app._post_process("Open the URL")
        assert "URL" in result

    def test_preserve_json(self, app):
        result = app._post_process("Parse JSON data")
        assert "JSON" in result


class TestCapitalization:
    """Test first-character capitalization."""

    def test_capitalize_first_char(self, app):
        result = app._post_process("hello world")
        assert result[0] == "H"

    def test_already_capitalized(self, app):
        result = app._post_process("Hello world")
        assert result == "Hello world"

    def test_empty_string(self, app):
        result = app._post_process("")
        assert result == ""


class TestRawMode:
    """Test that raw formatting mode skips all processing."""

    def test_raw_mode_no_changes(self, app):
        app.config.formatting_mode = "raw"
        result = app._post_process("hello DIR D-I-R")
        assert result == "hello DIR D-I-R"
