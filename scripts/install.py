#!/usr/bin/env python3
"""Cross-platform installer for DaVinci Resolve scripts.

Supports both macOS and Windows, automatically detecting the platform
and using the appropriate installation paths and commands.
"""

import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path


def get_install_dir() -> Path:
    """Get DaVinci Resolve scripts installation directory for the current platform."""
    system = platform.system()

    if system == "Darwin":  # macOS
        return Path.home() / "Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA environment variable not found")
        return Path(appdata) / "Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def get_venv_site_packages() -> str:
    """Get site-packages path from the current virtual environment."""
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-c", "import sys; print([p for p in sys.path if 'site-packages' in p][0] if any('site-packages' in p for p in sys.path) else '')"],
            capture_output=True,
            text=True,
            check=True,
        )
        site_packages = result.stdout.strip()
        if not site_packages:
            raise RuntimeError("Could not detect site-packages path")
        return site_packages
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to detect site-packages: {e}")


def check_environment() -> dict:
    """Check Python, uv, virtual environment, and required libraries."""
    print("=== Environment Check ===")
    print()

    checks = {"python": False, "uv": False, "venv": False, "libraries": {}}

    # Check Python
    print("1. Checking Python and uv...")
    try:
        python_version = subprocess.run(
            ["python3" if platform.system() != "Windows" else "python", "--version"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        print(f"✓ Python found: {python_version}")
        checks["python"] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Python not found")
        return checks

    try:
        uv_version = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        print(f"✓ uv found: {uv_version}")
        checks["uv"] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ uv not found (required for installation)")
        return checks

    # Check virtual environment and libraries
    print()
    print("2. Checking virtual environment and libraries...")
    try:
        site_packages = get_venv_site_packages()
        print(f"✓ Virtual environment found: {site_packages}")
        checks["venv"] = True
        checks["site_packages"] = site_packages
    except RuntimeError as e:
        print(f"✗ {e}")
        print("   Please run 'uv sync' to create virtual environment")
        return checks

    print()
    for lib in ["PIL", "rawpy", "exifread"]:
        try:
            subprocess.run(
                ["uv", "run", "python", "-c", f"import {lib}"],
                capture_output=True,
                check=True,
            )
            print(f"✓ {lib} installed")
            checks["libraries"][lib] = True
        except subprocess.CalledProcessError:
            print(f"✗ {lib} not found (run 'uv sync')")
            checks["libraries"][lib] = False

    # Check install directory
    print()
    print("3. Checking install directory...")
    install_dir = get_install_dir()
    if install_dir.exists():
        print(f"✓ Install directory exists: {install_dir}")
    else:
        print(f"! Install directory does not exist (will be created on install)")
        print(f"  {install_dir}")

    print()
    print("=== Check Complete ===")
    return checks


def install_script(script_path: Path, install_dir: Path, site_packages: str):
    """Install a single script with site-packages path embedded."""
    # Read source script
    content = script_path.read_text(encoding="utf-8")

    # Replace template placeholder with actual path
    # Match: VENV_PATH = "{{VENV_PATH}}"
    pattern = r'^VENV_PATH = "{{VENV_PATH}}"$'
    replacement = f'VENV_PATH = "{site_packages}"'
    modified_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Write to install directory
    target_path = install_dir / script_path.name
    target_path.write_text(modified_content, encoding="utf-8")
    print(f"Installed: {script_path.name}")


def install_simple_script(script_path: Path, install_dir: Path):
    """Install a script without dependency path embedding (for scripts without external dependencies)."""
    import shutil

    target_path = install_dir / script_path.name
    shutil.copy2(script_path, target_path)
    print(f"Installed: {script_path.name}")


def install():
    """Interactive installation of DaVinci Resolve scripts."""
    print("Select version to install:")
    print("  1) Free version (all Free scripts)")
    print("  2) Studio version (all Studio scripts)")

    choice = input("Enter choice [1-2]: ").strip()

    # Determine which scripts to install
    if choice == "1":
        scripts_with_deps = ["add_exif_frame_dv_lite.py"]
        scripts_simple = ["copy_project_settings_dv_lite.py"]
        version_name = "Free"
    elif choice == "2":
        scripts_with_deps = ["add_exif_frame_dv.py"]
        scripts_simple = ["copy_project_settings_dv.py"]
        version_name = "Studio"
    else:
        print("Invalid choice")
        sys.exit(1)

    print(f"\nInstalling {version_name} version scripts...")

    # Get install directory and create if needed
    install_dir = get_install_dir()
    install_dir.mkdir(parents=True, exist_ok=True)

    scripts_dir = Path(__file__).parent

    # Install scripts with dependencies (EXIF Frame scripts)
    if scripts_with_deps:
        # Get site-packages path
        try:
            site_packages = get_venv_site_packages()
        except RuntimeError as e:
            print(f"ERROR: {e}")
            print("Please run 'uv sync' first to create virtual environment.")
            sys.exit(1)

        print(f"Using site-packages: {site_packages}")

        for script_name in scripts_with_deps:
            script_path = scripts_dir / script_name
            if not script_path.exists():
                print(f"ERROR: Script not found: {script_path}")
                sys.exit(1)
            install_script(script_path, install_dir, site_packages)

    # Install scripts without dependencies (Copy Project Settings scripts)
    if scripts_simple:
        for script_name in scripts_simple:
            script_path = scripts_dir / script_name
            if not script_path.exists():
                print(f"ERROR: Script not found: {script_path}")
                sys.exit(1)
            install_simple_script(script_path, install_dir)

    print(f"\nInstallation complete ({version_name} version).")
    print("Installed scripts:")
    for script in scripts_with_deps + scripts_simple:
        print(f"  - {script}")
    print("\nPlease restart DaVinci Resolve if scripts do not appear.")


def uninstall():
    """Remove installed scripts from DaVinci Resolve."""
    install_dir = get_install_dir()

    scripts_to_remove = [
        "add_exif_frame_dv.py",
        "add_exif_frame_dv_lite.py",
    ]

    removed_count = 0
    for script_name in scripts_to_remove:
        script_path = install_dir / script_name
        if script_path.exists():
            script_path.unlink()
            print(f"Removed: {script_name}")
            removed_count += 1

    if removed_count > 0:
        print(f"Removed {removed_count} script(s) from {install_dir}")
    else:
        print(f"No scripts found in {install_dir}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/install.py install    - Install scripts")
        print("  python scripts/install.py uninstall  - Remove scripts")
        print("  python scripts/install.py check      - Check environment")
        sys.exit(1)

    command = sys.argv[1]

    if command == "install":
        install()
    elif command == "uninstall":
        uninstall()
    elif command == "check":
        checks = check_environment()
        # Exit with error if critical checks failed
        if not all([checks.get("python"), checks.get("uv"), checks.get("venv")]):
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
