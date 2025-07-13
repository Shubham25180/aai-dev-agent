#!/usr/bin/env python3
"""
main_simple.py - Minimal/Dev Mode Entry Point

This script starts the agent in simple mode (no LLM, no voice, no API server).
Use only for lightweight, offline, or development scenarios.
For full backend startup, use main.py.
"""

import sys
import signal
import threading
import time
from typing import Dict, Any
from app.bootstrap import Bootstrap
from utils.logger import get_action_logger, get_error_logger

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
    
    sys.exit(0)

def main():
    """
    Main application entry point - Simple mode without LLM dependencies.
    """
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize logging
    logger = get_action_logger('main', subsystem='core')
    error_logger = get_error_logger('main', subsystem='core')
    
    logger.info("Starting AI Dev Agent in simple mode (no LLM required)")
    
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
        
        # Display bootstrap success
        print("✅ AI Dev Agent initialized successfully in simple mode!")
        print(f"📊 Memory Stats: {bootstrap_result.get('memory_stats', {})}")
        print(f"🔧 Components: {bootstrap_result.get('components', {})}")
        
        # Get system status
        status = bootstrap.get_system_status()
        print(f"📈 System Status: {status.get('bootstrap_completed', False)}")
        
        # Show available features
        print("\n🚀 nexus Simple Mode Features:")
        print("   📝 File operations (create, edit, delete)")
        print("   🖥️  Shell command execution")
        print("   💾 Memory management")
        print("   ↩️  Undo/redo system")
        print("   📊 Task planning and routing")
        print("   🔒 Safety validation")
        print("   📝 Logging and monitoring")
        
        # Main interaction loop
        logger.info("System ready for task processing")
        print("\n🚀 nexus is ready! You can:")
        print("   📝 Type commands below")
        print("   💬 Ask for help or status")
        print("   ❌ Type 'exit' or 'quit' to stop")
        print("-" * 60)
        
        # Keep the application running with text input
        try:
            while True:
                # Ask for text input
                print("\n💬 Enter your command or task:")
                user_input = input("> ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'stop', 'bye']:
                    print("👋 Goodbye! Shutting down nexus...")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Process text input through controller
                print(f"\n🤖 Processing: '{user_input}'")
                
                try:
                    response = controller.process_task(user_input, {
                        'safety_level': 'high',
                        'simple_mode': True
                    })
                    
                    # Display response
                    if response.get('success'):
                        print(f"\n✅ Success: {response.get('message', 'Task completed')}")
                        
                        # Show details if available
                        if response.get('details'):
                            print(f"📋 Details: {response['details']}")
                        
                        if response.get('files_affected'):
                            print(f"📁 Files: {response['files_affected']}")
                        
                        if response.get('commands_executed'):
                            print(f"🖥️  Commands: {response['commands_executed']}")
                    
                    else:
                        print(f"\n❌ Error: {response.get('error', 'Unknown error')}")
                        
                        # Show suggestions if available
                        if response.get('suggestions'):
                            print(f"💡 Suggestions: {response['suggestions']}")
                
                except Exception as e:
                    logger.error(f"Error processing task: {e}")
                    print(f"\n❌ Processing error: {e}")
                
                print("-" * 60)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            print("\n👋 Shutting down nexus...")
        
        return 0
        
    except Exception as e:
        error_logger.error(f"Application failed: {e}", exc_info=True)
        print(f"❌ Application failed: {e}")
        return 1
    
    finally:
        # Ensure graceful shutdown
        if 'bootstrap' in locals():
            bootstrap.shutdown()
        logger.info("AI Dev Agent shutdown complete")

if __name__ == "__main__":
    # === Simple/dev mode only. For full backend, use main.py ===
    exit_code = main()
    sys.exit(exit_code) 