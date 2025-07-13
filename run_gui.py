#!/usr/bin/env python3
"""
NEXUS GUI Launcher - Simple wrapper for main.py

This is just a convenience script that calls main.py.
The real entry point is main.py which orchestrates everything.
"""

import sys
import os

def main():
    """Simple launcher that calls main.py."""
    print("🚀 Starting NEXUS AI Agent...")
    print("=" * 50)
    
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    try:
        # Import and run the main entry point
        from main import main as nexus_main
        nexus_main()
    except Exception as e:
        print(f"❌ Failed to start NEXUS: {e}")
        print("\nFull error:")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 