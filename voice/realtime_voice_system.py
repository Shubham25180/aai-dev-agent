#!/usr/bin/env python3
"""
Real-Time Voice System - Multi-threaded Pipeline
Continuous listening with parallel processing for Alexa/Siri-like responsiveness.
"""

import threading
import queue
import time
import numpy as np
import sounddevice as sd
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json
import os

# Import our existing components
from .recognizer import Recognizer
from .responder import Responder
from .commands import CommandProcessor
from utils.logger import get_action_logger, get_error_logger

@dataclass
class AudioChunk:
    """Audio chunk with metadata."""
    data: np.ndarray
    timestamp: float
    sample_rate: int
    duration: float

@dataclass
class TranscriptionResult:
    """Transcription result with confidence."""
    text: str
    confidence: float
    language: str
    timestamp: float
    is_command: bool

class RealTimeVoiceSystem:
    """
    Real-time voice system with multi-threaded pipeline:
    
    1. 🎧 Microphone Input Thread - Continuous audio streaming
    2. 📝 Transcription Thread - Live audio to text conversion
    3. 🎯 Command Detection Thread - Intent classification
    4. 🧠 LLM Processing Thread - Async task processing
    5. 🔊 TTS Output Thread - Non-blocking speech synthesis
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.logger = get_action_logger('realtime_voice')
        self.error_logger = get_error_logger('realtime_voice')
        
        # Audio configuration
        self.sample_rate = self.config.get('voice', {}).get('sample_rate', 16000)
        self.chunk_duration = self.config.get('voice', {}).get('chunk_duration', 0.5)  # seconds
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        self.channels = 1
        
        # Threading and queues
        self.audio_queue = queue.Queue(maxsize=100)
        self.transcription_queue = queue.Queue(maxsize=50)
        self.command_queue = queue.Queue(maxsize=20)
        self.llm_queue = queue.Queue(maxsize=10)
        self.tts_queue = queue.Queue(maxsize=10)
        
        # Thread control
        self.is_running = False
        self.threads = {}
        
        # Components
        self.recognizer = None
        self.responder = None
        self.command_processor = None
        self.llm_processor = None
        
        # Performance tracking
        self.stats = {
            'audio_chunks_processed': 0,
            'transcriptions_completed': 0,
            'commands_detected': 0,
            'llm_responses': 0,
            'tts_outputs': 0,
            'avg_audio_latency': 0,
            'avg_transcription_latency': 0,
            'avg_llm_latency': 0,
            'avg_tts_latency': 0
        }
        
        # Wake word detection
        self.wake_word = self.config.get('voice', {}).get('wake_word', 'nova')
        self.wake_word_enabled = self.config.get('voice', {}).get('wake_word_enabled', True)
        
        # Voice activity detection
        self.vad_threshold = self.config.get('voice', {}).get('vad_threshold', 0.01)
        self.silence_duration = self.config.get('voice', {}).get('silence_duration', 1.0)
        
        self.logger.info("RealTimeVoiceSystem initialized")

    async def start(self) -> bool:
        """Start the real-time voice system."""
        try:
            self.logger.info("Starting RealTimeVoiceSystem...")
            
            # Initialize components
            await self._initialize_components()
            
            # Start all threads
            self.is_running = True
            
            # Thread 1: Audio Input
            self.threads['audio_input'] = threading.Thread(
                target=self._audio_input_loop,
                daemon=True,
                name="AudioInput"
            )
            self.threads['audio_input'].start()
            
            # Thread 2: Transcription
            self.threads['transcription'] = threading.Thread(
                target=self._transcription_loop,
                daemon=True,
                name="Transcription"
            )
            self.threads['transcription'].start()
            
            # Thread 3: Command Detection
            self.threads['command_detection'] = threading.Thread(
                target=self._command_detection_loop,
                daemon=True,
                name="CommandDetection"
            )
            self.threads['command_detection'].start()
            
            # Thread 4: LLM Processing
            self.threads['llm_processing'] = threading.Thread(
                target=self._llm_processing_loop,
                daemon=True,
                name="LLMProcessing"
            )
            self.threads['llm_processing'].start()
            
            # Thread 5: TTS Output
            self.threads['tts_output'] = threading.Thread(
                target=self._tts_output_loop,
                daemon=True,
                name="TTSOutput"
            )
            self.threads['tts_output'].start()
            
            # Thread 6: Performance Monitor
            self.threads['performance_monitor'] = threading.Thread(
                target=self._performance_monitor_loop,
                daemon=True,
                name="PerformanceMonitor"
            )
            self.threads['performance_monitor'].start()
            
            self.logger.info("RealTimeVoiceSystem started successfully")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to start RealTimeVoiceSystem: {e}", exc_info=True)
            return False

    async def stop(self) -> bool:
        """Stop the real-time voice system."""
        try:
            self.logger.info("Stopping RealTimeVoiceSystem...")
            
            # Stop all threads
            self.is_running = False
            
            # Wait for threads to finish
            for thread_name, thread in self.threads.items():
                if thread.is_alive():
                    thread.join(timeout=5)
                    if thread.is_alive():
                        self.logger.warning(f"Thread {thread_name} did not stop gracefully")
            
            # Clear queues
            self._clear_queues()
            
            self.logger.info("RealTimeVoiceSystem stopped successfully")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to stop RealTimeVoiceSystem: {e}", exc_info=True)
            return False

    async def _initialize_components(self):
        """Initialize voice processing components."""
        try:
            # Initialize Whisper recognizer
            voice_config = self.config.get('voice', {})
            self.recognizer = Recognizer(
                model_size=voice_config.get('model_size', 'base.en'),
                device=voice_config.get('device', 'cpu'),
                compute_type=voice_config.get('compute_type', 'int8')
            )
            
            # Initialize TTS responder
            self.responder = Responder(
                rate=voice_config.get('tts_rate', 180),
                volume=voice_config.get('tts_volume', 1.0)
            )
            
            # Initialize command processor
            self.command_processor = CommandProcessor(
                commands=voice_config.get('commands', [])
            )
            
            # Initialize LLM processor (will be set externally)
            self.llm_processor = None
            
            self.logger.info("Voice components initialized successfully")
            
        except Exception as e:
            self.error_logger.error(f"Failed to initialize components: {e}", exc_info=True)
            raise

    def set_llm_processor(self, llm_processor: Callable):
        """Set the LLM processor function."""
        self.llm_processor = llm_processor

    def _audio_input_loop(self):
        """Thread 1: Continuous audio input streaming."""
        try:
            self.logger.info("Audio input thread started")
            
            def audio_callback(indata, frames, time, status):
                """Audio callback for real-time streaming."""
                if status:
                    self.logger.warning(f"Audio callback status: {status}")
                
                if self.is_running:
                    # Create audio chunk
                    chunk = AudioChunk(
                        data=indata.copy(),
                        timestamp=time.time(),
                        sample_rate=self.sample_rate,
                        duration=frames / self.sample_rate
                    )
                    
                    # Check for voice activity
                    if self._detect_voice_activity(chunk.data):
                        try:
                            self.audio_queue.put_nowait(chunk)
                            self.stats['audio_chunks_processed'] += 1
                        except queue.Full:
                            self.logger.warning("Audio queue full, dropping chunk")
            
            # Start audio stream
            with sd.InputStream(
                callback=audio_callback,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                dtype=np.float32
            ) as stream:
                self.logger.info("Audio stream started")
                
                while self.is_running:
                    time.sleep(0.1)  # Small sleep to prevent busy waiting
                
                self.logger.info("Audio stream stopped")
                
        except Exception as e:
            self.error_logger.error(f"Audio input loop error: {e}", exc_info=True)

    def _transcription_loop(self):
        """Thread 2: Live audio transcription."""
        try:
            self.logger.info("Transcription thread started")
            
            while self.is_running:
                try:
                    # Get audio chunk with timeout
                    chunk = self.audio_queue.get(timeout=1.0)
                    
                    start_time = time.time()
                    
                    # Transcribe audio chunk
                    transcription = self.recognizer.transcribe_audio(chunk.data)
                    
                    if transcription and transcription.get('text', '').strip():
                        # Create transcription result
                        result = TranscriptionResult(
                            text=transcription.get('text', '').strip(),
                            confidence=transcription.get('confidence', 0.0),
                            language=transcription.get('language', 'en'),
                            timestamp=chunk.timestamp,
                            is_command=self._is_command(transcription.get('text', ''))
                        )
                        
                        # Add to transcription queue
                        try:
                            self.transcription_queue.put_nowait(result)
                            self.stats['transcriptions_completed'] += 1
                            
                            # Update latency stats
                            latency = time.time() - start_time
                            self.stats['avg_transcription_latency'] = (
                                (self.stats['avg_transcription_latency'] * (self.stats['transcriptions_completed'] - 1) + latency) 
                                / self.stats['transcriptions_completed']
                            )
                            
                        except queue.Full:
                            self.logger.warning("Transcription queue full, dropping result")
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.error_logger.error(f"Transcription error: {e}")
                    
        except Exception as e:
            self.error_logger.error(f"Transcription loop error: {e}", exc_info=True)

    def _command_detection_loop(self):
        """Thread 3: Command detection and intent classification."""
        try:
            self.logger.info("Command detection thread started")
            
            while self.is_running:
                try:
                    # Get transcription result with timeout
                    result = self.transcription_queue.get(timeout=1.0)
                    
                    # Check if it's a command
                    if result.is_command:
                        try:
                            self.command_queue.put_nowait(result)
                            self.stats['commands_detected'] += 1
                            
                            self.logger.info(f"Command detected: {result.text}")
                            
                        except queue.Full:
                            self.logger.warning("Command queue full, dropping command")
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.error_logger.error(f"Command detection error: {e}")
                    
        except Exception as e:
            self.error_logger.error(f"Command detection loop error: {e}", exc_info=True)

    def _llm_processing_loop(self):
        """Thread 4: Asynchronous LLM processing."""
        try:
            self.logger.info("LLM processing thread started")
            
            while self.is_running:
                try:
                    # Get command with timeout
                    command = self.command_queue.get(timeout=1.0)
                    
                    if self.llm_processor:
                        start_time = time.time()
                        
                        try:
                            # Process with LLM (non-blocking)
                            response = asyncio.run(self.llm_processor(command.text))
                            
                            if response:
                                # Add to TTS queue
                                try:
                                    self.tts_queue.put_nowait({
                                        'text': response.get('content', ''),
                                        'command': command.text,
                                        'timestamp': time.time()
                                    })
                                    self.stats['llm_responses'] += 1
                                    
                                    # Update latency stats
                                    latency = time.time() - start_time
                                    self.stats['avg_llm_latency'] = (
                                        (self.stats['avg_llm_latency'] * (self.stats['llm_responses'] - 1) + latency) 
                                        / self.stats['llm_responses']
                                    )
                                    
                                except queue.Full:
                                    self.logger.warning("TTS queue full, dropping response")
                            
                        except Exception as e:
                            self.error_logger.error(f"LLM processing error: {e}")
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.error_logger.error(f"LLM processing loop error: {e}")
                    
        except Exception as e:
            self.error_logger.error(f"LLM processing loop error: {e}", exc_info=True)

    def _tts_output_loop(self):
        """Thread 5: Non-blocking TTS output."""
        try:
            self.logger.info("TTS output thread started")
            
            while self.is_running:
                try:
                    # Get TTS request with timeout
                    tts_request = self.tts_queue.get(timeout=1.0)
                    
                    start_time = time.time()
                    
                    # Speak the response
                    self.responder.speak(tts_request['text'])
                    
                    self.stats['tts_outputs'] += 1
                    
                    # Update latency stats
                    latency = time.time() - start_time
                    self.stats['avg_tts_latency'] = (
                        (self.stats['avg_tts_latency'] * (self.stats['tts_outputs'] - 1) + latency) 
                        / self.stats['tts_outputs']
                    )
                    
                    self.logger.info(f"TTS output: {tts_request['text'][:50]}...")
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.error_logger.error(f"TTS output error: {e}")
                    
        except Exception as e:
            self.error_logger.error(f"TTS output loop error: {e}", exc_info=True)

    def _performance_monitor_loop(self):
        """Thread 6: Performance monitoring and stats."""
        try:
            self.logger.info("Performance monitor thread started")
            
            while self.is_running:
                try:
                    # Log performance stats every 30 seconds
                    time.sleep(30)
                    
                    self.logger.info("Performance Stats:", extra={
                        'audio_chunks': self.stats['audio_chunks_processed'],
                        'transcriptions': self.stats['transcriptions_completed'],
                        'commands': self.stats['commands_detected'],
                        'llm_responses': self.stats['llm_responses'],
                        'tts_outputs': self.stats['tts_outputs'],
                        'avg_transcription_latency': f"{self.stats['avg_transcription_latency']:.3f}s",
                        'avg_llm_latency': f"{self.stats['avg_llm_latency']:.3f}s",
                        'avg_tts_latency': f"{self.stats['avg_tts_latency']:.3f}s"
                    })
                    
                except Exception as e:
                    self.error_logger.error(f"Performance monitor error: {e}")
                    
        except Exception as e:
            self.error_logger.error(f"Performance monitor loop error: {e}", exc_info=True)

    def _detect_voice_activity(self, audio_data: np.ndarray) -> bool:
        """Detect voice activity in audio chunk."""
        try:
            # Calculate RMS (Root Mean Square) energy
            rms = np.sqrt(np.mean(audio_data**2))
            
            # Check if energy is above threshold
            return rms > self.vad_threshold
            
        except Exception as e:
            self.error_logger.error(f"Voice activity detection error: {e}")
            return False

    def _is_command(self, text: str) -> bool:
        """Check if transcribed text is a command."""
        try:
            text_lower = text.lower().strip()
            
            # Check for wake word if enabled
            if self.wake_word_enabled and self.wake_word.lower() in text_lower:
                return True
            
            # Check for command patterns
            command_patterns = [
                'open', 'create', 'edit', 'delete', 'run', 'save', 'undo',
                'kholo', 'banane', 'edit', 'delete', 'chalane', 'save', 'undo'
            ]
            
            return any(pattern in text_lower for pattern in command_patterns)
            
        except Exception as e:
            self.error_logger.error(f"Command detection error: {e}")
            return False

    def _clear_queues(self):
        """Clear all queues."""
        try:
            while not self.audio_queue.empty():
                self.audio_queue.get_nowait()
            
            while not self.transcription_queue.empty():
                self.transcription_queue.get_nowait()
            
            while not self.command_queue.empty():
                self.command_queue.get_nowait()
            
            while not self.llm_queue.empty():
                self.llm_queue.get_nowait()
            
            while not self.tts_queue.empty():
                self.tts_queue.get_nowait()
                
        except Exception as e:
            self.error_logger.error(f"Error clearing queues: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get system status and performance metrics."""
        return {
            'active': self.is_running,
            'threads': {
                name: thread.is_alive() 
                for name, thread in self.threads.items()
            },
            'queue_sizes': {
                'audio': self.audio_queue.qsize(),
                'transcription': self.transcription_queue.qsize(),
                'command': self.command_queue.qsize(),
                'llm': self.llm_queue.qsize(),
                'tts': self.tts_queue.qsize()
            },
            'performance_stats': self.stats.copy(),
            'configuration': {
                'sample_rate': self.sample_rate,
                'chunk_duration': self.chunk_duration,
                'wake_word': self.wake_word,
                'wake_word_enabled': self.wake_word_enabled,
                'vad_threshold': self.vad_threshold
            }
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics."""
        return {
            'throughput': {
                'audio_chunks_per_second': self.stats['audio_chunks_processed'] / max(1, time.time() - self.start_time if hasattr(self, 'start_time') else 1),
                'transcriptions_per_second': self.stats['transcriptions_completed'] / max(1, time.time() - self.start_time if hasattr(self, 'start_time') else 1),
                'commands_per_second': self.stats['commands_detected'] / max(1, time.time() - self.start_time if hasattr(self, 'start_time') else 1)
            },
            'latency': {
                'avg_transcription_latency': self.stats['avg_transcription_latency'],
                'avg_llm_latency': self.stats['avg_llm_latency'],
                'avg_tts_latency': self.stats['avg_tts_latency'],
                'total_pipeline_latency': self.stats['avg_transcription_latency'] + self.stats['avg_llm_latency'] + self.stats['avg_tts_latency']
            },
            'counts': self.stats.copy()
        } 