#!/usr/bin/env python3
"""
Quick setup script for Memofarm backend
"""
import os
import sys
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...\n")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment found")
    else:
        print("⚠️  Virtual environment not found")
        print("   Run: python -m venv venv")
    
    # Check if .env file exists
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found")
        print("   Copy .env.example to .env and configure")
    
    # Check if confezioni.csv exists
    csv_path = Path("confezioni.csv")
    if csv_path.exists():
        print(f"✅ confezioni.csv found ({csv_path.stat().st_size / (1024*1024):.1f} MB)")
    else:
        print("⚠️  confezioni.csv not found")
        print("   Place the Italian medicine CSV file in the backend directory")
    
    return True

def show_next_steps():
    """Show next steps for setup"""
    print("\n" + "="*60)
    print("📋 Next Steps:")
    print("="*60)
    print()
    print("1. Activate virtual environment:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Linux/Mac: source venv/bin/activate")
    print()
    print("2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("3. Configure .env file:")
    print("   Copy .env.example to .env")
    print("   Add your MongoDB URI and OAuth credentials")
    print()
    print("4. Import Italian medicine database:")
    print("   python import_medicines.py")
    print()
    print("5. Start the server:")
    print("   python run.py")
    print()
    print("="*60)

if __name__ == "__main__":
    print("🚀 Memofarm Backend Setup\n")
    check_prerequisites()
    show_next_steps()
