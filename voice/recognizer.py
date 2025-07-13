import os
import queue
import threading
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
from utils.logger import get_action_logger, get_error_logger
try:
    import noisereduce as nr
    NOISE_REDUCE_AVAILABLE = True
except ImportError:
    NOISE_REDUCE_AVAILABLE = False

class Recognizer:
    """
    Speech recognizer using Whisper (offline) with multi-language support.
    Supports English, Indian English, Hindi with automatic language detection.
    Provides start/stop, confidence scoring, and comprehensive logging.
    """
    def __init__(self, model_size='medium', device='cpu', compute_type='int8'):
        self.logger = get_action_logger('voice_recognizer')
        self.error_logger = get_error_logger('voice_recognizer')
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        self.audio_queue = queue.Queue()
        self.running = False
        self.thread = None
        self.sample_rate = 16000
        self._load_model()

    def _load_model(self):
        """Load Whisper model with specified configuration."""
        try:
            print("[DEBUG] Recognizer: Loading Whisper model...", self.model_size, self.device)
            self.logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            self.model = WhisperModel(
                model_size_or_path=self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=None,  # Use default cache directory
                local_files_only=False  # Allow download if not cached
            )
            print("[DEBUG] Recognizer: Whisper model loaded successfully.")
            self.logger.info(f"Whisper {self.model_size} model loaded successfully")
        except Exception as e:
            print("[DEBUG] Recognizer: Failed to load Whisper model:", e)
            self.error_logger.error(f"Failed to load Whisper model: {e}")
            raise

    def _audio_callback(self, indata, frames, time, status):
        """Audio callback for real-time processing with noise reduction then normalization."""
        if status:
            self.error_logger.error(f"Audio status: {status}")
        # Convert to float32 and scale
        audio_data = indata.copy().astype(np.float32) / 32768.0
        # Noise reduction (simple, per chunk)
        if NOISE_REDUCE_AVAILABLE:
            try:
                audio_data = nr.reduce_noise(y=audio_data.flatten(), sr=self.sample_rate)
            except Exception as e:
                self.logger.warning(f"Noise reduction failed: {e}")
        # Peak normalization (after noise reduction)
        peak = np.max(np.abs(audio_data))
        if peak > 0:
            audio_data = audio_data / peak
        self.audio_queue.put(audio_data)

    def start(self):
        """Start real-time speech recognition."""
        if not self.model:
            print("[DEBUG] Recognizer: Model not loaded in start()!")
            self.logger.error("Whisper model not loaded")
            return False
        print("[DEBUG] Recognizer: Starting recognition thread...")
        self.running = True
        self.thread = threading.Thread(target=self._recognize_loop)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info("Real-time speech recognition started")
        print("[DEBUG] Recognizer: Recognition thread started.")
        return True

    def stop(self):
        """Stop speech recognition."""
        print("[DEBUG] Recognizer: Stopping recognition...")
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        self.logger.info("Speech recognition stopped")
        print("[DEBUG] Recognizer: Recognition stopped.")

    def _recognize_loop(self):
        """Main recognition loop for real-time processing with VAD buffering (2s silence)."""
        print("[DEBUG] Recognizer: Entered recognition loop (VAD buffering mode).")
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype=np.float32,
                channels=1,
                callback=self._audio_callback
            ):
                self.logger.info("Audio stream started")
                print("[DEBUG] Recognizer: Audio stream started.")
                buffer = np.array([], dtype=np.float32)
                silence_threshold = 0.01  # Amplitude below this is considered silence
                silence_duration_sec = 2.0
                silence_samples = int(self.sample_rate * silence_duration_sec)
                while self.running:
                    try:
                        audio_chunk = self.audio_queue.get(timeout=1.0)
                        print("[DEBUG] Recognizer: Got audio chunk.")
                        buffer = np.concatenate([buffer, audio_chunk.flatten()])
                        # Check for 2s of silence at the end of the buffer
                        if buffer.shape[0] >= silence_samples:
                            tail = buffer[-silence_samples:]
                            if np.max(np.abs(tail)) < silence_threshold:
                                # Found 2s of silence, process buffer up to this point
                                utterance = buffer[:-silence_samples]
                                if utterance.shape[0] > 0:
                                    print("[DEBUG] Recognizer: 2s silence detected, processing utterance.")
                                    # Noise reduction on full utterance
                                    if NOISE_REDUCE_AVAILABLE:
                                        try:
                                            utterance = nr.reduce_noise(y=utterance, sr=self.sample_rate)
                                        except Exception as e:
                                            self.logger.warning(f"Noise reduction failed on utterance: {e}")
                                    # Peak normalization (after noise reduction)
                                    peak = np.max(np.abs(utterance))
                                    if peak > 0:
                                        utterance = utterance / peak
                                    # Send utterance to Whisper for transcription
                                    if self.model is not None:
                                        segments, info = self.model.transcribe(
                                            utterance,
                                            beam_size=1,
                                            language=None,
                                            task="transcribe",
                                            vad_filter=False  # Already chunked by VAD
                                        )
                                        transcript = " ".join([seg.text for seg in segments])
                                        print(f"[TRANSCRIPT] {transcript.strip()}")
                                        self.logger.info(f"[TRANSCRIPT] {transcript.strip()}")
                                    else:
                                        self.logger.error("Whisper model is not loaded!")
                                # Remove processed audio from buffer
                                buffer = buffer[-silence_samples:]
                    except queue.Empty:
                        continue
        except Exception as e:
            print("[DEBUG] Recognizer: Recognition loop error:", e)
            self.error_logger.error(f"Recognition loop error: {e}")

    def recognize_once(self, duration=5.0) -> dict:
        """
        Recognize a single utterance (blocking).
        Returns transcript, confidence, and detected language.
        
        Args:
            duration: Recording duration in seconds
        """
        if not self.model:
            return {'success': False, 'error': 'Model not loaded'}
        
        try:
            self.logger.info(f"Listening for {duration} seconds...")
            
            # Record audio in smaller chunks to avoid memory issues
            chunk_duration = min(duration, 2.0)  # Max 2 seconds per chunk
            total_samples = int(duration * self.sample_rate)
            chunk_samples = int(chunk_duration * self.sample_rate)
            
            audio_data = np.array([], dtype=np.float32)
            
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=chunk_samples
            ) as stream:
                remaining_samples = total_samples
                
                while remaining_samples > 0:
                    samples_to_read = min(chunk_samples, remaining_samples)
                    chunk, _ = stream.read(samples_to_read)
                    audio_data = np.concatenate([audio_data, chunk.flatten()])
                    remaining_samples -= samples_to_read
            
            # Process with Whisper using optimized settings
            segments, info = self.model.transcribe(
                audio_data,
                beam_size=1,  # Reduce beam size for memory efficiency
                language=None,  # Auto-detect language
                task="transcribe",
                vad_filter=True,  # Use voice activity detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Get the full transcript
            transcript = ""
            confidence_scores = []
            
            for segment in segments:
                transcript += segment.text + " "
                confidence_scores.append(segment.avg_logprob)
            
            transcript = transcript.strip()
            
            # Calculate average confidence
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            # Convert log probability to confidence (0-1 scale)
            confidence = np.exp(avg_confidence) if avg_confidence < 0 else 1.0
            
            # Get detected language
            detected_language = info.language if hasattr(info, 'language') else 'unknown'
            language_probability = info.language_probability if hasattr(info, 'language_probability') else 0.0
            
            result = {
                'success': True,
                'text': transcript,
                'confidence': float(confidence),
                'language': detected_language,
                'language_probability': float(language_probability),
                'duration': duration
            }
            
            self.logger.info(
                f"Recognized: '{transcript}' (lang: {detected_language}, conf: {confidence:.2f})",
                extra={
                    'confidence': confidence,
                    'language': detected_language,
                    'language_probability': language_probability
                }
            )
            
            return result
            
        except Exception as e:
            self.error_logger.error(f"Single recognition error: {e}")
            return {'success': False, 'error': str(e)}

    def recognize_file(self, audio_file_path: str) -> dict:
        """
        Recognize speech from an audio file.
        
        Args:
            audio_file_path: Path to the audio file
        """
        if not self.model:
            return {'success': False, 'error': 'Model not loaded'}
        
        if not os.path.exists(audio_file_path):
            return {'success': False, 'error': f'Audio file not found: {audio_file_path}'}
        
        try:
            self.logger.info(f"Processing audio file: {audio_file_path}")
            
            segments, info = self.model.transcribe(
                audio_file_path,
                beam_size=1,  # Reduce beam size for memory efficiency
                language=None,  # Auto-detect language
                task="transcribe",
                vad_filter=True
            )
            
            # Get the full transcript
            transcript = ""
            confidence_scores = []
            
            for segment in segments:
                transcript += segment.text + " "
                confidence_scores.append(segment.avg_logprob)
            
            transcript = transcript.strip()
            
            # Calculate average confidence
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            confidence = np.exp(avg_confidence) if avg_confidence < 0 else 1.0
            
            # Get detected language
            detected_language = info.language if hasattr(info, 'language') else 'unknown'
            language_probability = info.language_probability if hasattr(info, 'language_probability') else 0.0
            
            result = {
                'success': True,
                'text': transcript,
                'confidence': float(confidence),
                'language': detected_language,
                'language_probability': float(language_probability),
                'file_path': audio_file_path
            }
            
            self.logger.info(
                f"File recognized: '{transcript}' (lang: {detected_language}, conf: {confidence:.2f})",
                extra={
                    'confidence': confidence,
                    'language': detected_language,
                    'language_probability': language_probability,
                    'file_path': audio_file_path
                }
            )
            
            return result
            
        except Exception as e:
            self.error_logger.error(f"File recognition error: {e}")
            return {'success': False, 'error': str(e)}

    def get_supported_languages(self) -> list:
        """Get list of supported languages."""
        return [
            'en',      # English
            'hi',      # Hindi
            'auto'     # Auto-detect
        ]

    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        if not self.model:
            return {'error': 'Model not loaded'}
        
        return {
            'model_size': self.model_size,
            'device': self.device,
            'compute_type': self.compute_type,
            'sample_rate': self.sample_rate,
            'supported_languages': self.get_supported_languages()
        } 