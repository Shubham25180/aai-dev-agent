import numpy as np
from faster_whisper import WhisperModel

class FasterWhisperSTT:
    """
    Speech-to-text engine using Faster-Whisper INT8 for fast, accurate transcription.
    Supports file and buffer input. Designed for real-time use in Nexus.
    """
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        """
        Initialize the Faster-Whisper model.
        Args:
            model_size (str): Model size ("tiny", "base", "small", "medium", "large-v2")
            device (str): "cpu" or "cuda"
            compute_type (str): Quantization type ("int8" for best speed)
        """
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio_path, beam_size=1):
        """
        Transcribe an audio file.
        Args:
            audio_path (str): Path to audio file (wav, mp3, etc.)
            beam_size (int): Beam search size (1 = greedy, faster)
        Returns:
            List of segments (dict with start, end, text, words, confidence)
        """
        segments, info = self.model.transcribe(audio_path, beam_size=beam_size)
        results = []
        for seg in segments:
            results.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text,
                "words": getattr(seg, "words", None),
                "confidence": getattr(seg, "avg_logprob", None)
            })
        return results

    def transcribe_buffer(self, audio: np.ndarray, beam_size=1, sample_rate=16000):
        """
        Transcribe a numpy audio buffer.
        Args:
            audio (np.ndarray): Audio waveform (mono, float32)
            beam_size (int): Beam search size
            sample_rate (int): Audio sample rate (default 16kHz)
        Returns:
            List of segments (dict)
        """
        # Ensure audio is always 16kHz before calling this method!
        segments, info = self.model.transcribe(audio, beam_size=beam_size)
        results = []
        for seg in segments:
            results.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text,
                "words": getattr(seg, "words", None),
                "confidence": getattr(seg, "avg_logprob", None)
            })
        return results

    # TODO: Add streaming/real-time chunked transcription for always-on use
    # TODO: Add language detection, VAD integration, and error handling 