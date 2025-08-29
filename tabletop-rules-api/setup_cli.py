#!/usr/bin/env python3
"""
Setup script for Tabletop Rules CLI

This script installs the CLI dependencies and sets up the environment
for optimal content management workflow.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_cli_requirements():
    """Install CLI-specific requirements."""
    print("🔧 Installing CLI requirements...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "cli_requirements.txt"
        ])
        print("✅ CLI requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install CLI requirements: {e}")
        return False

def make_cli_executable():
    """Make the CLI script executable."""
    cli_path = Path("tabletop_cli.py")
    if cli_path.exists():
        # Make executable on Unix systems
        if os.name != 'nt':  # Not Windows
            os.chmod(cli_path, 0o755)
        print("✅ CLI script made executable")
        return True
    else:
        print("❌ CLI script not found")
        return False

def test_cli_installation():
    """Test that the CLI can be imported and run."""
    print("🧪 Testing CLI installation...")
    try:
        # Test import
        import typer
        import httpx
        import rich
        print("✅ All CLI dependencies imported successfully")
        
        # Test CLI script syntax
        result = subprocess.run([
            sys.executable, "tabletop_cli.py", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ CLI script syntax is valid")
            return True
        else:
            print(f"❌ CLI script has syntax errors:\n{result.stderr}")
            return False
            
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ CLI script took too long to respond")
        return False
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def create_cli_alias():
    """Create a convenient alias for the CLI."""
    cli_path = Path("tabletop_cli.py").absolute()
    alias_content = f"""
# Add this to your shell profile (.bashrc, .zshrc, etc.)
alias tabletop="python {cli_path}"

# Or create a symlink (requires sudo):
# sudo ln -s {cli_path} /usr/local/bin/tabletop
"""
    
    print("💡 CLI Alias Setup:")
    print(alias_content)
    
    # Try to detect shell and provide specific instructions
    shell = os.environ.get('SHELL', '').split('/')[-1]
    if shell in ['bash', 'zsh']:
        profile_file = f".{shell}rc" if shell == 'bash' else f".{shell}rc"
        print(f"💡 To add permanently, run:")
        print(f'echo "alias tabletop=\\"python {cli_path}\\"" >> ~/{profile_file}')

def main():
    """Main setup function."""
    print("🎲 Tabletop Rules CLI Setup")
    print("=" * 40)
    
    success = True
    
    # Check if we're in the right directory
    if not Path("tabletop_cli.py").exists():
        print("❌ Please run this script from the tabletop-rules-api directory")
        sys.exit(1)
    
    # Install requirements
    if not install_cli_requirements():
        success = False
    
    # Make CLI executable
    if not make_cli_executable():
        success = False
    
    # Test installation
    if not test_cli_installation():
        success = False
    
    if success:
        print("\n🎉 CLI Setup Complete!")
        print("\nQuick start:")
        print("  python tabletop_cli.py status")
        print("  python tabletop_cli.py list-games")
        print("  python tabletop_cli.py upload rules_data/chess_rules.md")
        print("\nFor more commands:")
        print("  python tabletop_cli.py --help")
        
        create_cli_alias()
    else:
        print("\n❌ CLI Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()