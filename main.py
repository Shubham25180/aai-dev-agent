#!/usr/bin/env python3
"""
AI Dev Agent - Main Entry Point
A memory-aware, undo-capable, proactive AI developer assistant with real-time voice support.
Now featuring the Real-Time Voice System - Your Alexa/Siri-like AI Development Friend!
"""

import sys
import signal
import threading
import time
from typing import Dict, Any
from app.bootstrap import Bootstrap
from voice.realtime_voice_system import RealTimeVoiceSystem
from agents.conversational_brain import ConversationalBrain
from agents.hybrid_llm_connector import HybridLLMConnector
from utils.logger import get_action_logger, get_error_logger
import asyncio
import requests
import queue
from voice.listener import MicListener
from voice.wake_word import WakeWordDetector
from voice.transcriber import RealTimeTranscriber
from voice.responder import TTSResponder
from context_pipeline import analyze_emotion  # Reuse emotion logic
from voice.always_on_listener import AlwaysOnListener
import subprocess

def signal_handler(signum, frame):
    """
    Handle shutdown signals gracefully.
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    logger = get_action_logger('main', subsystem='core')
    logger.info(f"Received signal {signum}, shutting down gracefully")
    
    # Get bootstrap instance and shutdown
    if hasattr(signal_handler, 'bootstrap') and signal_handler.bootstrap:
        signal_handler.bootstrap.shutdown()
    
    # Stop real-time voice system if running
    if hasattr(signal_handler, 'voice_system') and signal_handler.voice_system:
        asyncio.run(signal_handler.voice_system.stop())
    
    sys.exit(0)

async def process_voice_with_llm(text: str, language: str, llm_connector) -> Dict[str, Any]:
    """
    Process voice input with hybrid LLM strategy.
    
    Args:
        text: Recognized voice text
        language: Detected language
        llm_connector: Hybrid LLM connector
        
    Returns:
        dict: LLM processing result
    """
    try:
        # Classify task complexity
        task_type = classify_task_complexity(text)
        
        # Process with hybrid LLM connector
        response = await llm_connector.send_prompt(
            text,
            task_type=task_type,
            temperature=0.7,
            max_tokens=200
        )
        
        return {
            'success': response.get('success', False),
            'content': response.get('content', ''),
            'model_used': response.get('routing_info', {}).get('backend_used', 'unknown'),
            'task_type': task_type,
            'response_time': response.get('response_time', 0)
        }
        
    except Exception as e:
        logger = get_action_logger('voice_llm', subsystem='voice')
        logger.error(f"Error processing voice with LLM: {e}")
        return {'success': False, 'error': str(e)}

def classify_task_complexity(text: str) -> str:
    """Classify task complexity to determine which model to use."""
    # Simple task keywords
    simple_keywords = [
        'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
        'how are you', 'what time', 'what date', 'weather', 'temperature',
        'open', 'close', 'save', 'delete', 'undo', 'redo', 'stop', 'start',
        'yes', 'no', 'okay', 'sure', 'thanks', 'thank you', 'bye', 'goodbye',
        'status', 'check', 'list', 'show', 'display'
    ]
    
    # Complex task keywords
    complex_keywords = [
        'write', 'create', 'generate', 'code', 'function', 'algorithm',
        'explain', 'analyze', 'compare', 'discuss', 'describe', 'define',
        'solve', 'calculate', 'implement', 'design', 'plan', 'strategy',
        'why', 'how does', 'what is the difference', 'pros and cons',
        'story', 'narrative', 'creative', 'imagine', 'think about',
        'optimize', 'debug', 'refactor', 'architecture', 'system',
        'search', 'find', 'look up', 'research', 'information about'
    ]
    
    text_lower = text.lower()
    
    # Count matches
    simple_matches = sum(1 for keyword in simple_keywords if keyword in text_lower)
    complex_matches = sum(1 for keyword in complex_keywords if keyword in text_lower)
    
    # Determine task type
    if complex_matches > simple_matches:
        return 'complex'
    else:
        return 'simple'

def voice_command_handler(command_result: Dict[str, Any], controller) -> Dict[str, Any]:
    """
    Handle voice commands by routing them to the appropriate executor and LLM processing.
    
    Args:
        command_result: Result from voice command processing
        controller: Main application controller
        
    Returns:
        dict: Execution result
    """
    logger = get_action_logger('voice_handler', subsystem='voice')
    
    try:
        command = command_result.get('command')
        args = command_result.get('args', [])
        action = command_result.get('action', '')
        language = command_result.get('language', 'en')
        text = command_result.get('text', '')
        
        logger.info(f"Processing voice command: {command} ({action})", extra={
            'args': args,
            'language': language,
            'text': text
        })
        
        # Map voice commands to controller actions
        if command == 'open_file':
            if args:
                return controller.process_task(f"Open file: {args[0]}", {
                    'safety_level': 'high',
                    'voice_command': True
                })
            else:
                return {'success': False, 'error': 'No file specified', 'voice_command': True}
        
        elif command == 'create_file':
            if args:
                return controller.process_task(f"Create file: {args[0]}", {
                    'safety_level': 'high',
                    'voice_command': True
                })
            else:
                return {'success': False, 'error': 'No file specified', 'voice_command': True}
        
        elif command == 'edit_file':
            if args:
                return controller.process_task(f"Edit file: {args[0]}", {
                    'safety_level': 'high',
                    'voice_command': True
                })
            else:
                return {'success': False, 'error': 'No file specified', 'voice_command': True}
        
        elif command == 'delete_file':
            if args:
                return controller.process_task(f"Delete file: {args[0]}", {
                    'safety_level': 'high',
                    'voice_command': True,
                    'require_confirmation': True
                })
            else:
                return {'success': False, 'error': 'No file specified', 'voice_command': True}
        
        elif command == 'run_command':
            if args:
                return controller.process_task(f"Run command: {args[0]}", {
                    'safety_level': 'medium',
                    'voice_command': True
                })
            else:
                return {'success': False, 'error': 'No command specified', 'voice_command': True}
        
        elif command == 'save':
            return controller.process_task("Save all files", {
                'safety_level': 'high',
                'voice_command': True
            })
        
        elif command == 'undo':
            return controller.process_task("Undo last action", {
                'safety_level': 'high',
                'voice_command': True
            })
        
        elif command == 'exit':
            logger.info("Voice command: Exit requested")
            return {'success': True, 'action': 'exit_requested'}
        
        # Git operations
        elif command == 'git_commit':
            return controller.process_task("Commit changes to git", {
                'safety_level': 'medium',
                'voice_command': True
            })
        
        elif command == 'git_push':
            return controller.process_task("Push to remote repository", {
                'safety_level': 'medium',
                'voice_command': True
            })
        
        elif command == 'git_pull':
            return controller.process_task("Pull from remote repository", {
                'safety_level': 'medium',
                'voice_command': True
            })
        
        # Testing operations
        elif command == 'run_tests':
            return controller.process_task("Run all tests", {
                'safety_level': 'medium',
                'voice_command': True
            })
        
        elif command == 'debug':
            return controller.process_task("Start debugging session", {
                'safety_level': 'medium',
                'voice_command': True
            })
        
        # Navigation
        elif command == 'navigate':
            if args:
                return controller.process_task(f"Navigate to: {args[0]}", {
                    'safety_level': 'high',
                    'voice_command': True
                })
            else:
                return {'success': False, 'error': 'No destination specified', 'voice_command': True}
        
        elif command == 'navigate_up':
            return controller.process_task("Navigate to parent directory", {
                'safety_level': 'high',
                'voice_command': True
            })
        
        # Search
        elif command == 'search':
            if args:
                return controller.process_task(f"Search for: {args[0]}", {
                    'safety_level': 'high',
                    'voice_command': True
                })
            else:
                return {'success': False, 'error': 'No search term specified', 'voice_command': True}
        
        # Documentation
        elif command == 'create_docs':
            return controller.process_task("Create documentation", {
                'safety_level': 'high',
                'voice_command': True
            })
        
        elif command == 'edit_readme':
            return controller.process_task("Edit README file", {
                'safety_level': 'high',
                'voice_command': True
            })
        
        else:
            logger.warning(f"Unknown voice command: {command}")
            return {
                'success': False,
                'error': f"Unknown command: {command}",
                'voice_command': True
            }
    
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        return {
            'success': False,
            'error': str(e),
            'voice_command': True
        }

async def real_time_voice_monitor(voice_system, controller, llm_connector):
    """
    Monitor real-time voice system and display performance metrics.
    
    Args:
        voice_system: Real-time voice system instance
        controller: Main application controller
        llm_connector: Hybrid LLM connector
    """
    logger = get_action_logger('voice_monitor', subsystem='voice')
    
    logger.info("Starting real-time voice system monitor")
    
    try:
        while voice_system.is_active:
            # Get system status
            status = voice_system.get_status()
            metrics = voice_system.get_performance_metrics()
            
            # Display real-time metrics
            print(f"\n🎤 Real-Time Voice System Status:")
            print(f"   Active Threads: {sum(1 for is_alive in status['threads'].values() if is_alive)}/{len(status['threads'])}")
            print(f"   Audio Queue: {status['queue_sizes']['audio']}")
            print(f"   Transcription Queue: {status['queue_sizes']['transcription']}")
            print(f"   Command Queue: {status['queue_sizes']['command']}")
            print(f"   LLM Queue: {status['queue_sizes']['llm']}")
            print(f"   TTS Queue: {status['queue_sizes']['tts']}")
            
            print(f"\n⚡ Performance Metrics:")
            print(f"   Audio Chunks/sec: {metrics['throughput']['audio_chunks_per_second']:.1f}")
            print(f"   Transcriptions/sec: {metrics['throughput']['transcriptions_per_second']:.1f}")
            print(f"   Commands/sec: {metrics['throughput']['commands_per_second']:.1f}")
            print(f"   Total Pipeline Latency: {metrics['latency']['total_pipeline_latency']:.3f}s")
            
            # Check performance targets
            targets = controller.config.get('performance_targets', {}).get('voice', {})
            
            if metrics['latency']['total_pipeline_latency'] > targets.get('max_total_latency', 3.0):
                print(f"⚠️  Latency exceeds target: {metrics['latency']['total_pipeline_latency']:.3f}s > {targets.get('max_total_latency', 3.0)}s")
            
            if metrics['throughput']['audio_chunks_per_second'] < targets.get('min_throughput', 10):
                print(f"⚠️  Throughput below target: {metrics['throughput']['audio_chunks_per_second']:.1f} < {targets.get('min_throughput', 10)}")
            
            # Wait before next check
            await asyncio.sleep(10)
            
    except Exception as e:
        logger.error(f"Voice monitor error: {e}")

WAKE_WORD = "nexus"
AUDIO_BUFFER_SECONDS = 3  # How much audio to buffer after wake word

class NexusVoiceOrchestrator:
    def __init__(self):
        self.listener = MicListener()
        self.wake_detector = WakeWordDetector(wake_word=WAKE_WORD)
        self.transcriber = RealTimeTranscriber()
        self.tts = TTSResponder()
        self.audio_queue = queue.Queue()
        self.running = True

    def mic_thread(self):
        self.listener.start()
        for chunk in self.listener.get_audio_chunk():
            self.audio_queue.put(chunk)
            if not self.running:
                break

    def main_loop(self):
        print("[Nexus] Always-on voice system started. Listening to everything...")
        while self.running:
            chunk = self.audio_queue.get()
            self.transcriber.add_chunk(chunk)
            transcript = self.transcriber.transcribe_buffer()
            if transcript.strip():
                print(f"[Nexus] Transcript: {transcript}")
                if "nexus" in transcript.lower():
                    print("[Nexus] (COMMAND DETECTED!) You addressed me directly.")
            if not self.running:
                break

    def run(self):
        mic_thread = threading.Thread(target=self.mic_thread, daemon=True)
        mic_thread.start()
        try:
            self.main_loop()
        except KeyboardInterrupt:
            print("[Nexus] Shutting down...")
            self.running = False
            self.listener.stop()

# --- Text mode fallback (existing logic) ---
def text_mode():
    print("[Nexus] Text mode activated. Type your commands below.")
    # ... existing text input loop ...
    while True:
        user_input = input("💬 Enter your command, question, or task:\n> ")
        if user_input.strip().lower() in ["exit", "quit"]:
            print("[Nexus] Exiting text mode.")
            break
        # TODO: Integrate with ConversationalBrain and TTS
        print(f"[Nexus] (Stub) You typed: {user_input}")

# --- Ollama auto-start logic ---
def ensure_ollama_running():
    ollama_url = "http://localhost:11434"
    try:
        # Try to ping Ollama API
        r = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if r.status_code == 200:
            print("[NEXUS] Ollama is already running.")
            return
    except Exception:
        print("[NEXUS] Ollama not running. Starting Ollama server...")
        try:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[NEXUS] Failed to start Ollama: {e}")
            sys.exit(1)
        # Wait for Ollama to be ready
        for i in range(20):
            try:
                r = requests.get(f"{ollama_url}/api/tags", timeout=2)
                if r.status_code == 200:
                    print("[NEXUS] Ollama started successfully.")
                    return
            except Exception:
                time.sleep(1)
        print("[NEXUS] Warning: Ollama did not start in time. LLM requests may fail.")

# Ensure Ollama is running before anything else
ensure_ollama_running()

def main():
    """
    Main application entry point with real-time voice integration.
    """
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize logging
    logger = get_action_logger('main', subsystem='core')
    error_logger = get_error_logger('main', subsystem='core')
    
    logger.info("Starting AI Dev Agent with real-time voice support")
    
    try:
        # Initialize bootstrap system
        bootstrap = Bootstrap()
        signal_handler.bootstrap = bootstrap  # Store for signal handler
        
        # Bootstrap the application
        bootstrap_result = bootstrap.bootstrap_application()
        
        if not bootstrap_result.get('success', False):
            error_logger.error("Bootstrap failed", extra=bootstrap_result)
            print(f"❌ Bootstrap failed: {bootstrap_result.get('error', 'Unknown error')}")
            return 1
        
        # Get the controller for task processing
        controller = bootstrap.get_component('controller')
        if not controller:
            error_logger.error("Controller not available after bootstrap")
            print("❌ Controller not available after bootstrap")
            return 1
        
        # Initialize hybrid LLM connector
        llm_connector = HybridLLMConnector(bootstrap_result.get('config', {}))
        llm_success = asyncio.run(llm_connector.start())
        
        if not llm_success:
            print("❌ Failed to initialize LLM connector")
            return 1
        
        # Initialize real-time voice system
        voice_system = RealTimeVoiceSystem(bootstrap_result.get('config', {}))
        signal_handler.voice_system = voice_system  # Store for signal handler
        
        # Set LLM processor for voice system
        voice_system.set_llm_processor(lambda text: asyncio.run(process_voice_with_llm(text, 'en', llm_connector)))
        
        # Display bootstrap success
        print("✅ AI Dev Agent initialized successfully!")
        print(f"📊 Memory Stats: {bootstrap_result.get('memory_stats', {})}")
        print(f"🔧 Components: {bootstrap_result.get('components', {})}")
        
        # Get system status
        status = bootstrap.get_system_status()
        print(f"📈 System Status: {status.get('bootstrap_completed', False)}")
        
        # Start real-time voice system if enabled
        voice_config = bootstrap_result.get('config', {}).get('voice', {})
        if voice_config.get('enabled', False):
            print("\n🎤 Starting real-time voice system...")
            voice_success = asyncio.run(voice_system.start())
            
            if voice_success:
                print("✅ Real-time voice system started successfully!")
                print("🧵 Multi-threaded pipeline active:")
                print("   • Audio Input Thread")
                print("   • Transcription Thread")
                print("   • Command Detection Thread")
                print("   • LLM Processing Thread")
                print("   • TTS Output Thread")
                print("   • Performance Monitor Thread")
                
                print("\n🎯 Voice Commands Available:")
                print("   • 'Nexus, open main.py'")
                print("   • 'Nexus, create new function'")
                print("   • 'Nexus, run tests'")
                print("   • 'Nexus, save all files'")
                print("   • 'Nexus, undo last action'")
                
                # Start voice monitor in background
                voice_monitor_thread = threading.Thread(
                    target=lambda: asyncio.run(real_time_voice_monitor(voice_system, controller, llm_connector)),
                    daemon=True
                )
                voice_monitor_thread.start()
                
                print("\n📊 Real-time performance monitoring active...")
            else:
                print("❌ Failed to start real-time voice system")
        
        # Initialize conversational brain
        conversational_brain = ConversationalBrain(bootstrap_result.get('config', {}))
        # Inject edge-tts responder from voice_system
        if hasattr(voice_system, 'responder') and voice_system.responder:
            conversational_brain.set_tts_responder(voice_system.responder)
        if conversational_brain.start():
            print("🧠 Conversational Brain activated!")
        
        # Show TTS status
        if conversational_brain.tts_enabled:
            print("🔊 Text-to-Speech: Enabled - Nexus will speak responses!")
        else:
            print("🔇 Text-to-Speech: Disabled - Nexus will only display text")
        
        # Main interaction loop
        logger.info("System ready for task processing")
        print("\n🚀 Nexus is ready! You can:")
        print("   📝 Type commands below")
        print("   🎤 Speak voice commands (if voice enabled)")
        print("   🔊 Hear Nexus speak responses (if TTS enabled)")
        print("   💬 Ask questions or request help")
        print("   ❌ Type 'exit' or 'quit' to stop")
        print("-" * 60)
        
        # Ask user for mode
        mode = input("Select mode: [1] Voice (always-on)  [2] Text (type commands)\nEnter 1 for Voice, 2 for Text [default: 1]: ").strip()
        if mode == "2":
            text_mode()
            return
        # --- Always-On Voice Mode ---
        always_on = AlwaysOnListener(conversational_brain=conversational_brain)
        always_on.run()
        
        return 0
        
    except Exception as e:
        error_logger.error(f"Application failed: {e}", exc_info=True)
        print(f"❌ Application failed: {e}")
        return 1
    
    finally:
        # Ensure graceful shutdown
        if 'bootstrap' in locals():
            bootstrap.shutdown()
        if 'voice_system' in locals():
            asyncio.run(voice_system.stop())
        if 'llm_connector' in locals():
            asyncio.run(llm_connector.stop())
        logger.info("AI Dev Agent shutdown complete")

if __name__ == "__main__":
    main() 