"""Unit tests for AppConfig settings management."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from config import AppConfig


@pytest.fixture
def tmp_settings_dir(tmp_path):
    """Provide a temporary directory for settings."""
    return str(tmp_path)


class TestConfigDefaults:
    """Test that default config values are sensible."""

    def test_default_hotkey(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        assert config.hotkey == {"ctrl", "alt", "space"}

    def test_default_model(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        assert config.model_name == "small.en"

    def test_default_sample_rate(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        assert config.sample_rate == 16000

    def test_default_recording_mode(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        assert config.recording_mode == "toggle"

    def test_default_formatting_mode(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        assert config.formatting_mode == "cleaned"

    def test_default_sounds_enabled(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        assert config.play_sounds is True


class TestConfigSaveLoad:
    """Test saving and loading settings to/from disk."""

    def test_save_creates_file(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        config.save()
        assert os.path.exists(config.settings_file)

    def test_save_load_roundtrip(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        config.model_name = "medium.en"
        config.recording_mode = "push_to_talk"
        config.play_sounds = False
        config.save()

        config2 = AppConfig(_settings_dir=tmp_settings_dir)
        config2.load()
        assert config2.model_name == "medium.en"
        assert config2.recording_mode == "push_to_talk"
        assert config2.play_sounds is False

    def test_hotkey_serialization(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        config.hotkey = {"ctrl", "shift", "f1"}
        config.save()

        config2 = AppConfig(_settings_dir=tmp_settings_dir)
        config2.load()
        assert config2.hotkey == {"ctrl", "shift", "f1"}

    def test_load_missing_file_uses_defaults(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        config.load()  # No file exists yet
        assert config.model_name == "small.en"
        assert config.hotkey == {"ctrl", "alt", "space"}

    def test_load_corrupted_file_uses_defaults(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        with open(config.settings_file, "w") as f:
            f.write("not valid json{{{")
        config.load()
        assert config.model_name == "small.en"

    def test_load_ignores_unknown_keys(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        with open(config.settings_file, "w") as f:
            json.dump({"model_name": "tiny.en", "fake_key": "fake_value"}, f)
        config.load()
        assert config.model_name == "tiny.en"
        assert not hasattr(config, "fake_key")

    def test_save_excludes_settings_dir(self, tmp_settings_dir):
        config = AppConfig(_settings_dir=tmp_settings_dir)
        config.save()
        with open(config.settings_file) as f:
            data = json.load(f)
        assert "_settings_dir" not in data
