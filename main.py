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

def signal_handler(signum, frame):
    """
    Handle shutdown signals gracefully.
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    logger = get_action_logger('main')
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
        logger = get_action_logger('voice_llm')
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
    logger = get_action_logger('voice_handler')
    
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
    logger = get_action_logger('voice_monitor')
    
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

def main():
    """
    Main application entry point with real-time voice integration.
    """
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize logging
    logger = get_action_logger('main')
    error_logger = get_error_logger('main')
    
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
                print("   • 'Nova, open main.py'")
                print("   • 'Nova, create new function'")
                print("   • 'Nova, run tests'")
                print("   • 'Nova, save all files'")
                print("   • 'Nova, undo last action'")
                
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
        if conversational_brain.start():
            print("🧠 Conversational Brain activated!")
        
        # Show TTS status
        if conversational_brain.tts_enabled:
            print("🔊 Text-to-Speech: Enabled - NOVA will speak responses!")
        else:
            print("🔇 Text-to-Speech: Disabled - NOVA will only display text")
        
        # Main interaction loop
        logger.info("System ready for task processing")
        print("\n🚀 NOVA is ready! You can:")
        print("   📝 Type commands below")
        print("   🎤 Speak voice commands (if voice enabled)")
        print("   🔊 Hear NOVA speak responses (if TTS enabled)")
        print("   💬 Ask questions or request help")
        print("   ❌ Type 'exit' or 'quit' to stop")
        print("-" * 60)
        
        # Keep the application running with text input
        try:
            while True:
                # Ask for text input
                print("\n💬 Enter your command, question, or task:")
                user_input = input("> ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'stop', 'bye']:
                    print("👋 Goodbye! Shutting down NOVA...")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Process text input through conversational brain
                print(f"\n🤖 Processing: '{user_input}'")
                response = conversational_brain.process_input(user_input, 'text')
                
                # Display response
                if response.get('text'):
                    print(f"\n💡 NOVA Response:")
                    print(f"{response['text']}")
                    
                    # Speak the response using TTS
                    try:
                        if conversational_brain.tts_enabled:
                            print("🔊 Speaking response...")
                            conversational_brain.speak_response(response['text'])
                    except Exception as e:
                        logger.warning(f"TTS failed: {e}")
                    
                    # Show which model was used
                    if response.get('model_used'):
                        print(f"\n🧠 Model used: {response['model_used']}")
                    
                    # Show confidence if available
                    if response.get('confidence'):
                        print(f"📊 Confidence: {response['confidence']:.1%}")
                    
                    # Show web search info if used
                    if response.get('web_search_used'):
                        print("🌐 Web search used for real-time information")
                
                # Handle errors
                if response.get('error'):
                    print(f"\n❌ Error: {response['error']}")
                
                print("-" * 60)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            print("\n👋 Shutting down NOVA...")
        
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
    exit_code = main()
    sys.exit(exit_code) 