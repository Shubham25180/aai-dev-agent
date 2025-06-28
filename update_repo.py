#!/usr/bin/env python3
"""
Update Repository Script
Easy way to update your Hugging Face repository with local changes.
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def main():
    """Main update function."""
    print("🚀 AI Dev Agent - Repository Update Tool")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found. Please run this script from the ai_dev_agent directory.")
        sys.exit(1)
    
    print(f"📅 Update started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check Hugging Face CLI
    print("\n🔍 Checking Hugging Face CLI...")
    hf_cli_path = r"C:\Users\shubh\AppData\Roaming\Python\Python313\Scripts\huggingface-cli.exe"
    
    if not os.path.exists(hf_cli_path):
        print("❌ Hugging Face CLI not found at expected location.")
        print("Please install it with: pip install -U 'huggingface_hub[cli]'")
        sys.exit(1)
    
    print("✅ Hugging Face CLI found")
    
    # Step 2: Check login status
    print("\n🔐 Checking login status...")
    if not run_command(f'"{hf_cli_path}" whoami', "Checking login status"):
        print("❌ Not logged in. Please run: huggingface-cli login")
        sys.exit(1)
    
    # Step 3: Upload to Hugging Face
    print("\n📤 Uploading to Hugging Face...")
    if run_command(f'"{hf_cli_path}" upload Shubham25180/ai .', "Uploading to Hugging Face"):
        print("\n🎉 Upload completed successfully!")
        print("🌐 Your updated repository is available at:")
        print("   https://huggingface.co/Shubham25180/ai")
        print("\n🧪 Test your changes at:")
        print("   https://huggingface.co/spaces/Shubham25180/ai")
    else:
        print("\n❌ Upload failed. Please check the error messages above.")
        sys.exit(1)
    
    # Step 4: Optional - Git commit (if git is available)
    print("\n📝 Checking for git repository...")
    if os.path.exists(".git"):
        print("Git repository found. Would you like to commit changes? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes']:
                commit_message = input("Enter commit message (or press Enter for default): ").strip()
                if not commit_message:
                    commit_message = f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                if run_command("git add .", "Adding files to git"):
                    if run_command(f'git commit -m "{commit_message}"', "Committing changes"):
                        print("✅ Git commit completed")
                        print("💡 To push to GitHub, run: git push origin main")
                    else:
                        print("⚠️ Git commit failed")
                else:
                    print("⚠️ Git add failed")
        except KeyboardInterrupt:
            print("\n⚠️ Git commit skipped")
    else:
        print("No git repository found. Skipping git operations.")
    
    print(f"\n📅 Update completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎯 Next steps:")
    print("   1. Visit your repository: https://huggingface.co/Shubham25180/ai")
    print("   2. Test the live demo: https://huggingface.co/spaces/Shubham25180/ai")
    print("   3. Share with others!")

if __name__ == "__main__":
    main() 