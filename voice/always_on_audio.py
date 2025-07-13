import threading
import queue
import time
import numpy as np
import sounddevice as sd
import webrtcvad
import noisereduce as nr
from voice.wake_word import WakeWordDetector
from faster_whisper import WhisperModel
from voice.transcript_processor import TranscriptProcessor
from typing import Callable, Optional

class AlwaysOnAudioPipeline:
    """
    Always-on audio pipeline with real-time VAD, noise reduction, normalization,
    wake word detection, Whisper transcription, and callback/queue for GUI integration.
    Now with continuous speech buffering to never miss any speech.
    """
    def __init__(self,
                 whisper_model_size='medium',  # Changed from 'base' to 'medium' for better accuracy
                 device='cpu',
                 sample_rate=16000,
                 vad_mode=3,
                 vad_frame_ms=30,
                 vad_speech_ms=100,
                 vad_silence_ms=500,
                 wake_word='nexus',
                 on_transcript: Optional[Callable[[str, float, float], None]] = None):
        """
        Args:
            whisper_model_size: Whisper model size (e.g., 'medium')
            device: 'cpu' or 'cuda'
            sample_rate: Audio sample rate
            vad_mode: webrtcvad aggressiveness (0-3)
            vad_frame_ms: Frame size for VAD (10, 20, or 30 ms)
            vad_speech_ms: Minimum speech length to trigger (ms)
            vad_silence_ms: Silence to end segment (ms)
            wake_word: Wake word to listen for
            on_transcript: Callback for (transcript, whisper_time, total_time)
        """
        self.sample_rate = sample_rate
        self.vad = webrtcvad.Vad(vad_mode)
        self.vad_frame_ms = vad_frame_ms
        self.vad_speech_frames = vad_speech_ms // vad_frame_ms
        self.vad_silence_frames = vad_silence_ms // vad_frame_ms
        self.audio_queue = queue.Queue()
        self.running = False
        self.thread = None
        self.wake_detector = WakeWordDetector(wake_word=wake_word)
        # Use int8 quantized model for fast CPU inference
        # Use absolute path to ensure model is found regardless of working directory
        import os
        whisper_model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'whisper-base-int8')
        self.whisper = WhisperModel(whisper_model_path, device=device)
        self.on_transcript = on_transcript
        self._in_speech = False
        self._speech_buffer = []
        self._silence_counter = 0
        self._wake_active = True  # Always collect speech; wake word is a future option
        
        # Speech buffering system
        self._processing_lock = threading.Lock()
        self._is_processing = False
        self._continuous_buffer = []  # Continuous buffer for all speech
        self._processing_buffer = []  # Buffer being processed
        self._new_speech_detected = False  # Flag for new speech during processing
        
        # Initialize transcript processor
        self.transcript_processor = TranscriptProcessor()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._audio_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

    def set_vad_mode(self, mode):
        """Set VAD aggressiveness mode (0-3)."""
        if 0 <= mode <= 3:
            self.vad = webrtcvad.Vad(mode)
            print(f"[AlwaysOnAudio] VAD mode set to {mode}")
        else:
            print(f"[AlwaysOnAudio] Invalid VAD mode: {mode} (must be 0-3)")

    def _audio_callback(self, indata, frames, time_info, status):
        # Convert to 16-bit PCM
        audio = (indata[:, 0] * 32768).astype(np.int16).tobytes()
        self.audio_queue.put(audio)

    def _audio_loop(self):
        frame_bytes = int(self.sample_rate * self.vad_frame_ms / 1000) * 2  # 16-bit mono
        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32', callback=self._audio_callback, blocksize=int(self.sample_rate * self.vad_frame_ms / 1000)):
            print("[AlwaysOnAudio] Listening...")
            while self.running:
                try:
                    frame = self.audio_queue.get(timeout=1)
                    if len(frame) != frame_bytes:
                        continue
                    is_speech = self.vad.is_speech(frame, self.sample_rate)
                    
                    if not self._wake_active:
                        audio_np = np.frombuffer(frame, dtype=np.int16).astype(np.float32) / 32768.0
                        wake_detected = self.wake_detector.process_chunk(audio_np)
                        if wake_detected:
                            print("[AlwaysOnAudio] Wake word detected!")
                            self._wake_active = True
                            self._speech_buffer = []
                            self._continuous_buffer = []
                            self._in_speech = False
                            self._silence_counter = 0
                        continue
                    
                    if is_speech:
                        print(f"[VAD][DEBUG] Speech detected, appending frame. Buffer size: {len(self._speech_buffer)+1}")
                        self._speech_buffer.append(frame)
                        self._continuous_buffer.append(frame)  # Add to continuous buffer
                        self._in_speech = True
                        self._silence_counter = 0
                        
                        # If we're currently processing, mark that new speech was detected
                        if self._is_processing:
                            self._new_speech_detected = True
                            print("[AlwaysOnAudio][DEBUG] New speech detected during processing - will concatenate")
                            
                    elif self._in_speech:
                        self._silence_counter += 1
                        if self._silence_counter > self.vad_silence_frames:
                            print("[VAD][DEBUG] End of speech segment detected.")
                            self._process_speech_segment()
                            self._in_speech = False
                            self._speech_buffer = []
                            self._silence_counter = 0
                            
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[AlwaysOnAudio][ERROR] Exception in audio loop: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

    def _process_speech_segment(self):
        """Process speech segment with continuous buffering."""
        if not self._speech_buffer:
            print("[DEBUG] No speech buffer to process.")
            return
            
        # Use lock to prevent multiple simultaneous processing
        with self._processing_lock:
            if self._is_processing:
                print("[AlwaysOnAudio][DEBUG] Already processing, adding to continuous buffer.")
                # Don't start new processing, just let the current one continue
                return
            self._is_processing = True
            self._new_speech_detected = False
            
        try:
            print("[AlwaysOnAudio] Starting speech processing...")
            
            # Process continuously until no new speech is detected
            while True:
                # Copy current continuous buffer for processing
                with self._processing_lock:
                    self._processing_buffer = self._continuous_buffer.copy()
                    self._new_speech_detected = False
                
                if not self._processing_buffer:
                    print("[AlwaysOnAudio][DEBUG] No speech to process.")
                    break
                    
                print(f"[AlwaysOnAudio][DEBUG] Processing {len(self._processing_buffer)} frames...")
                
                # Process the current buffer
                transcript = self._transcribe_buffer(self._processing_buffer)
                
                # Check if new speech was detected during processing
                with self._processing_lock:
                    if self._new_speech_detected:
                        print("[AlwaysOnAudio][DEBUG] New speech detected during processing, continuing...")
                        continue  # Process again with updated buffer
                    else:
                        print("[AlwaysOnAudio][DEBUG] No new speech detected, finalizing transcript.")
                        break
                        
        finally:
            # Always release the processing lock and clear buffers
            with self._processing_lock:
                self._is_processing = False
                self._continuous_buffer = []  # Clear the continuous buffer
                self._processing_buffer = []

    def _transcribe_buffer(self, audio_frames):
        """Transcribe a buffer of audio frames."""
        if not audio_frames:
            return ""
            
        # Concatenate frames
        audio_bytes = b''.join(audio_frames)
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        print(f"[NoiseReduction][DEBUG] Raw audio shape: {audio_np.shape}, dtype: {audio_np.dtype}")
        
        # Noise reduction
        try:
            audio_nr = nr.reduce_noise(y=audio_np, sr=self.sample_rate)
            print(f"[NoiseReduction][DEBUG] Noise reduction applied. Output shape: {audio_nr.shape}")
        except Exception as e:
            print(f"[AlwaysOnAudio] Noise reduction failed: {e}")
            audio_nr = audio_np
            
        # Normalization
        peak = np.max(np.abs(audio_nr))
        print(f"[Normalization][DEBUG] Peak value before normalization: {peak}")
        if peak > 0:
            audio_nr = audio_nr / peak
            print(f"[Normalization][DEBUG] Normalization applied. Max after: {np.max(np.abs(audio_nr))}")
        else:
            print(f"[Normalization][DEBUG] Skipped normalization (peak=0)")
            
        # Whisper transcription
        start_time = time.time()
        try:
            print(f"[Whisper][DEBUG] Starting transcription...")
            # Use better settings for accuracy, especially for proper nouns
            segments, info = self.whisper.transcribe(
                audio_nr, 
                beam_size=5,  # Increased from 1 for better accuracy
                language=None,  # Auto-detect language
                task="transcribe",
                condition_on_previous_text=False,  # Don't condition on previous text
                temperature=0.0,  # Use greedy decoding for consistency
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0
            )
            print(f"[Whisper][DEBUG] Transcription finished.")
        except Exception as e:
            print(f"[Whisper][ERROR] Exception during transcription: {e}")
            import traceback
            traceback.print_exc()
            return ""
            
        whisper_time = time.time() - start_time
        transcript = " ".join([seg.text for seg in segments]).strip()
        
        # Post-process transcript to fix common misrecognitions
        transcript = self.transcript_processor.process(transcript)
        
        print(f"[Whisper][DEBUG] Transcript: {transcript}")
        print(f"[Whisper][DEBUG] Whisper time: {whisper_time:.2f}s")
        
        # Callback to GUI
        if self.on_transcript and transcript:
            try:
                self.on_transcript(transcript, whisper_time, time.time() - start_time)
                print("[AlwaysOnAudio][DEBUG] on_transcript callback completed.")
            except Exception as e:
                print(f"[AlwaysOnAudio][ERROR] Exception in on_transcript callback: {e}")
                import traceback
                traceback.print_exc()
                
        return transcript 