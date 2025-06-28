#!/usr/bin/env python3
"""
AI Dev Agent - Main Entry Point
A memory-aware, undo-capable, proactive AI developer assistant.
"""

import sys
import signal
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
    logger = get_action_logger('main')
    logger.info(f"Received signal {signum}, shutting down gracefully")
    
    # Get bootstrap instance and shutdown
    if hasattr(signal_handler, 'bootstrap') and signal_handler.bootstrap:
        signal_handler.bootstrap.shutdown()
    
    sys.exit(0)

def main():
    """
    Main application entry point.
    """
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize logging
    logger = get_action_logger('main')
    error_logger = get_error_logger('main')
    
    logger.info("Starting AI Dev Agent")
    
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
        print("✅ AI Dev Agent initialized successfully!")
        print(f"📊 Memory Stats: {bootstrap_result.get('memory_stats', {})}")
        print(f"🔧 Components: {bootstrap_result.get('components', {})}")
        
        # Get system status
        status = bootstrap.get_system_status()
        print(f"📈 System Status: {status.get('bootstrap_completed', False)}")
        
        # Example task processing (can be replaced with actual user interaction)
        logger.info("System ready for task processing")
        print("\n🚀 System ready for task processing!")
        print("💡 Example: Use controller.process_task('your task here') to process tasks")
        
        # Keep the application running (in a real implementation, this would be a main loop)
        print("\n⏳ Press Ctrl+C to exit...")
        
        # Simple example task
        example_task = "Create a test file to verify system functionality"
        print(f"\n🧪 Processing example task: {example_task}")
        
        result = controller.process_task(example_task, {
            'safety_level': 'high',
            'verbose_logging': True
        })
        
        if result.get('success', False):
            print(f"✅ Task completed successfully!")
            print(f"📋 Steps completed: {result.get('completed_steps', 0)}/{result.get('total_steps', 0)}")
            print(f"⏱️  Execution time: {result.get('execution_time', 0)}s")
        else:
            print(f"❌ Task failed: {result.get('error_message', 'Unknown error')}")
        
        # Wait for user input or signal
        try:
            while True:
                # In a real implementation, this would be a proper event loop
                # For now, just keep the process alive
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        
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
    exit_code = main()
    sys.exit(exit_code) 