#!/usr/bin/env python3
"""Setup development environment.

Usage:
  python setup.py

What it does:
  1. Checks Python version (requires 3.11+)
  2. Checks uv is installed
  3. Creates .venv virtual environment
  4. Installs project dependencies (including dev)
  5. Installs pre-commit hooks (if configured)
  6. Verifies the installation works

Example output:
  ┌─────────────────────────────────────┐
  │ Development Environment Setup       │
  └─────────────────────────────────────┘

  Checking Python version...
    ✓ Python 3.12

  Checking uv is installed...
    ✓ uv 0.1.0

  Virtual environment exists
    ✓ .venv

  Installing dependencies...
    ✓ Done

  Verifying installation...
    ✓ Utils package working

  ════════════════════════════════════
  Setup completed successfully!

  Next steps:
    1. Activate the virtual environment: source .venv/bin/activate
    2. Run tests: python scripts/test.py
    3. Start coding!
"""

import argparse
import subprocess
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Path, Terminal


def get_project_root() -> PathLib:
    """Get the project root directory."""
    return PathLib(__file__).parent.parent


def run_step(description: str, cmd: list[str]) -> bool:
    """Run a setup step."""
    print(f"\n{Terminal.colorize(description, color='cyan', bold=True)}")
    result = subprocess.run(cmd, cwd=get_project_root())
    if result.returncode == 0:
        print(Terminal.colorize("  ✓ Done", color="green"))
        return True
    else:
        print(Terminal.colorize("  ✗ Failed", color="red"))
        return False


def check_python_version() -> bool:
    """Check Python version is 3.11+."""
    print(f"\n{Terminal.colorize('Checking Python version...', color='cyan', bold=True)}")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(Terminal.colorize(f"  ✓ Python {version.major}.{version.minor}", color="green"))
        return True
    else:
        print(Terminal.colorize(
            f"  ✗ Python 3.11+ required, found {version.major}.{version.minor}",
            color="red",
        ))
        return False


def check_uv_installed() -> bool:
    """Check if uv is installed."""
    print(f"\n{Terminal.colorize('Checking uv is installed...', color='cyan', bold=True)}")
    result = subprocess.run(["uv", "--version"], capture_output=True)
    if result.returncode == 0:
        version = result.stdout.decode().strip()
        print(Terminal.colorize(f"  ✓ {version}", color="green"))
        return True
    else:
        print(Terminal.colorize("  ✗ uv not found", color="red"))
        print("  Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False


def create_venv() -> bool:
    """Create virtual environment if it doesn't exist."""
    venv_path = get_project_root() / ".venv"
    if venv_path.exists():
        print(f"\n{Terminal.colorize('Virtual environment exists', color='cyan', bold=True)}")
        print(Terminal.colorize("  ✓ .venv", color="green"))
        return True
    return run_step("Creating virtual environment...", ["uv", "venv", ".venv"])


def install_dependencies() -> bool:
    """Install project dependencies."""
    return run_step(
        "Installing dependencies...",
        ["uv", "pip", "install", "-e", ".[dev]"],
    )


def install_precommit() -> bool:
    """Install pre-commit hooks."""
    precommit_config = get_project_root() / ".pre-commit-config.yaml"
    if not precommit_config.exists():
        print(f"\n{Terminal.colorize('No pre-commit config found', color='yellow', bold=True)}")
        return True
    return run_step("Installing pre-commit hooks...", ["pre-commit", "install"])


def verify_installation() -> bool:
    """Verify installation by running a quick test."""
    print(f"\n{Terminal.colorize('Verifying installation...', color='cyan', bold=True)}")
    result = subprocess.run(
        [sys.executable, "-c", "from utils import String; print(String.truncate('hello', length=3))"],
        cwd=get_project_root(),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip() == "hel":
        print(Terminal.colorize("  ✓ Utils package working", color="green"))
        return True
    else:
        print(Terminal.colorize("  ✗ Import test failed", color="red"))
        return False


def main() -> int:
    Terminal.print_box("Development Environment Setup")

    root = get_project_root()
    print(f"\nProject root: {root}")

    steps = [
        ("Python version", check_python_version),
        ("uv installed", check_uv_installed),
        ("Virtual environment", create_venv),
        ("Dependencies", install_dependencies),
        ("Pre-commit hooks", install_precommit),
        ("Verification", verify_installation),
    ]

    failed = []
    for name, step_func in steps:
        if not step_func():
            failed.append(name)

    print()
    Terminal.print_line("═", width=60)

    if failed:
        print(Terminal.colorize("Setup completed with errors:", color="yellow", bold=True))
        for name in failed:
            print(f"  - {name}")
        return 1
    else:
        print(Terminal.colorize("Setup completed successfully!", color="green", bold=True))
        print("\nNext steps:")
        print("  1. Activate the virtual environment: source .venv/bin/activate")
        print("  2. Run tests: python scripts/test.py")
        print("  3. Start coding!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
