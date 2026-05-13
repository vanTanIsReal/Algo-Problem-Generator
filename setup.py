#!/usr/bin/env python3
"""
Setup requirements and guide for training the problem generation model.
"""

import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install required packages."""
    
    print("=" * 60)
    print("Setup: Problem Generation Model Training Environment")
    print("=" * 60)
    
    # Check Python version
    print(f"\n✅ Python version: {sys.version.split()[0]}")
    
    # Required packages
    requirements = {
        "torch": "PyTorch - Deep Learning Framework",
        "transformers": "Hugging Face Transformers - Pre-trained models",
        "accelerate": "Accelerate training on multiple devices",
    }
    
    print("\n📦 Required packages:")
    for pkg, desc in requirements.items():
        print(f"   - {pkg}: {desc}")
    
    print("\n🔧 Installation options:")
    print("\n1️⃣  Install all at once:")
    print("   pip install torch transformers accelerate datasets")
    
    print("\n2️⃣  Or step by step:")
    print("   pip install torch")
    print("   pip install transformers")
    print("   pip install accelerate datasets")
    
    print("\n3️⃣  For GPU support (CUDA):")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    print("   pip install transformers accelerate datasets")
    
    print("\n⏱️  Installation may take 5-10 minutes...")
    print("\nAfter installation, run: python train/train.py")
    
    # Ask user
    response = input("\n❓ Install packages now? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\n⏳ Installing...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "torch", "transformers", "accelerate", "datasets"
            ])
            print("\n✅ Installation complete!")
            return True
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            print("Please install manually and try again")
            return False
    else:
        print("\n⏭️  Skipping installation. To train the model, install packages first.")
        return False


def create_setup_script():
    """Create setup.py for automated installation."""
    setup_content = """#!/usr/bin/env python3
import subprocess
import sys

packages = ['torch', 'transformers', 'accelerate', 'datasets']
for pkg in packages:
    print(f"Installing {pkg}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
print("✅ All packages installed!")
"""
    
    setup_file = Path("setup_environment.py")
    with open(setup_file, "w") as f:
        f.write(setup_content)
    
    print(f"\n📁 Created setup script: {setup_file}")
    print(f"   Run with: python {setup_file}")


def main():
    install_requirements()
    create_setup_script()


if __name__ == "__main__":
    main()
