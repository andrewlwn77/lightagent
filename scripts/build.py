# scripts/build.py
import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, check=True):
    """Run a command and return its output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()

def get_venv_python():
    """Get the Python executable from virtualenv."""
    if sys.platform == "win32":
        return Path(".venv/Scripts/python.exe")
    return Path(".venv/bin/python")

def setup_venv():
    """Create and setup virtualenv."""
    if not Path(".venv").exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        
    python = get_venv_python()
    # Upgrade pip
    run_cmd([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    return python

def install_dependencies(python, dev=False):
    """Install package dependencies."""
    cmd = [str(python), "-m", "pip", "install", "-e", "."]
    if dev:
        cmd[-1] = ".[dev]"
    run_cmd(cmd)

def clean():
    """Clean build artifacts."""
    patterns = [
        "build/", "dist/", "*.egg-info",
        "**/__pycache__", ".pytest_cache",
        ".coverage", "htmlcov/", ".mypy_cache"
    ]
    
    for pattern in patterns:
        for path in Path().glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

def run_tests(python):
    """Run tests with coverage."""
    run_cmd([
        str(python), "-m", "pytest",
        "tests/",
        "--cov=robotape",
        "--cov-report=term-missing"
    ])

def format_code(python):
    """Format code with black and isort."""
    run_cmd([str(python), "-m", "black", "src/", "tests/"])
    run_cmd([str(python), "-m", "isort", "src/", "tests/"])

def lint(python):
    """Run all linters."""
    run_cmd([str(python), "-m", "mypy", "src/"])
    run_cmd([str(python), "-m", "black", "--check", "src/", "tests/"])
    run_cmd([str(python), "-m", "flake8", "src/", "tests/"])

def main():
    """Main build script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build script for robotape")
    parser.add_argument("command", choices=[
        "install", "dev", "clean", "test",
        "format", "lint", "all"
    ])
    
    args = parser.parse_args()
    
    if args.command == "clean":
        clean()
        return
        
    python = setup_venv()
    
    if args.command == "install":
        install_dependencies(python)
    elif args.command == "dev":
        install_dependencies(python, dev=True)
    elif args.command == "test":
        run_tests(python)
    elif args.command == "format":
        format_code(python)
    elif args.command == "lint":
        lint(python)
    elif args.command == "all":
        clean()
        install_dependencies(python, dev=True)
        format_code(python)
        lint(python)
        run_tests(python)

if __name__ == "__main__":
    main()