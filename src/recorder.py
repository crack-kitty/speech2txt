"""Audio recording using sounddevice."""

import io
import threading
import wave
from typing import Optional

import numpy as np
import sounddevice as sd

from config import AppConfig


class AudioRecorder:
    """Records microphone audio into a WAV buffer."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._frames: list[np.ndarray] = []
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start capturing audio from the microphone."""
        with self._lock:
            self._frames = []
            self._stream = sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype="float32",
                device=self.config.audio_device,
                callback=self._audio_callback,
            )
            self._stream.start()

    def stop(self) -> bytes:
        """Stop recording and return WAV data as bytes."""
        with self._lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None

        if not self._frames:
            return b""

        audio = np.concatenate(self._frames, axis=0)
        duration = len(audio) / self.config.sample_rate
        print(f"Recorded {duration:.1f}s of audio")

        return self._to_wav_bytes(audio)

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: object,
        status: sd.CallbackFlags,
    ) -> None:
        """Called by sounddevice for each audio chunk."""
        if status:
            print(f"Audio status: {status}")
        self._frames.append(indata.copy())

    def _to_wav_bytes(self, audio: np.ndarray) -> bytes:
        """Convert float32 numpy array to WAV bytes."""
        # Convert float32 [-1, 1] to int16
        int16_audio = (audio * 32767).astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(self.config.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.config.sample_rate)
            wf.writeframes(int16_audio.tobytes())
        return buf.getvalue()

    @staticmethod
    def list_devices() -> list[dict]:
        """Return available audio input devices."""
        devices = sd.query_devices()
        inputs = []
        for i, d in enumerate(devices):
            if d["max_input_channels"] > 0:
                inputs.append({"index": i, "name": d["name"]})
        return inputs
