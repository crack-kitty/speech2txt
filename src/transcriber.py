"""Speech-to-text transcription using faster-whisper."""

import os
import threading
import time
from typing import Optional

import numpy as np

from faster_whisper import WhisperModel

from config import AppConfig


class Transcriber:
    """Loads a Whisper model and transcribes audio."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._model: Optional[WhisperModel] = None
        self._ready = threading.Event()
        self.current_model_name: str = ""

    def load_model(self) -> None:
        """Load the Whisper model. Call from a background thread."""
        print(f"Loading Whisper model '{self.config.model_name}'...")
        t0 = time.perf_counter()
        self._model = WhisperModel(
            self.config.model_name,
            device="cpu",
            compute_type="auto",
            cpu_threads=8,
        )
        elapsed = time.perf_counter() - t0
        self.current_model_name = self.config.model_name
        print(f"Model loaded in {elapsed:.1f}s")
        self._ready.set()

    @property
    def is_ready(self) -> bool:
        return self._ready.is_set()

    def wait_until_ready(self, timeout: float = 120.0) -> bool:
        """Block until the model is loaded."""
        return self._ready.wait(timeout=timeout)

    def transcribe(self, audio: np.ndarray) -> str:
        """Transcribe a float32 numpy audio array and return the text."""
        if not self._ready.is_set() or self._model is None:
            print("Model not ready yet")
            return ""

        if len(audio) == 0:
            return ""

        t0 = time.perf_counter()
        segments, info = self._model.transcribe(
            audio.flatten(),
            language="en",
            vad_filter=False,
        )

        text_parts: list[str] = []
        for segment in segments:
            text_parts.append(segment.text)

        result = " ".join(text_parts).strip()
        elapsed = time.perf_counter() - t0
        print(f"Transcribed in {elapsed:.2f}s: {result}")
        return result
