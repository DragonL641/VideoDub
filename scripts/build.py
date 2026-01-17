#!/usr/bin/env python3
"""Unified build script for VideoDub - handles both single-platform and cross-platform builds."""

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def load_build_config():
    """Load build configuration from JSON file."""
    config_path = Path("nuitka-build-config.json")
    if not config_path.exists():
        # Try relative path from scripts directory
        config_path = Path("../nuitka-build-config.json")
        if not config_path.exists():
            raise FileNotFoundError("Build configuration file not found")

    with open(config_path, "r") as f:
        return json.load(f)


def get_platform_specific_flags():
    """Get platform-specific Nuitka flags."""
    system = platform.system().lower()
    arch = platform.machine().lower()

    flags = [
        "--standalone",
        "--onefile",
        "--enable-console",
        "--remove-output",
        "--follow-imports",
        "--python-flag=no_site",
        "--python-flag=no_warnings",
        "--warn-unusual-code",
        "--assume-yes-for-downloads",
    ]

    # Platform-specific optimizations
    if system == "darwin":  # macOS
        flags.extend(
            [
                "--macos-create-app-bundle=no",  # Single executable file
                "--macos-app-icon=",
                "--macos-signed-app-name=VideoDub",
                "--include-package=torch",
                "--include-package=whisper",
                "--include-package=transformers",
            ]
        )
        # Handle Apple Silicon vs Intel
        if "arm" in arch:
            flags.append("--macos-target-arch=arm64")
        else:
            flags.append("--macos-target-arch=x86_64")

    elif system == "windows":
        flags.extend(
            [
                "--windows-uac-admin=no",
                "--windows-uac-uiaccess=no",
                "--windows-icon-from-ico=",
                "--windows-company-name=VideoDub",
                "--windows-product-name=VideoDub",
                "--windows-file-description=VideoDub - Automatic Subtitle Generator",
                "--windows-product-version=0.2.0.0",
                "--windows-legal-copyright=Copyright (c) 2024 VideoDub",
            ]
        )

    elif system == "linux":
        flags.extend(
            [
                "--linux-onefile-icon=",
            ]
        )

    # Include all required packages
    packages = [
        "ffmpeg",
        "psutil",
        "numpy",
        "sentencepiece",
        "accelerate",
        "torchaudio",
        "torchvision",
    ]

    for package in packages:
        flags.append(f"--include-package={package}")

    # Include data files
    flags.extend(
        [
            "--include-data-dir=src=src",
            "--include-data-files=README.md=README.md",
            "--include-data-files=LICENSE=LICENSE",
        ]
    )

    return flags


def build_executable(output_name=None):
    """Build the executable using Nuitka."""
    system = platform.system()
    machine = platform.machine()
    print(f"Building VideoDub for {system} ({machine})")

    # Load configuration
    config = load_build_config()
    main_module = config["main_module"]

    # Check if main module exists
    if not Path(main_module).exists():
        raise FileNotFoundError(f"Main module {main_module} not found")

    # Prepare build command
    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        main_module,
        "--output-dir=dist",
    ]

    # Set output filename if specified
    if output_name:
        cmd.append(f"--output-filename={output_name}")

    # Add platform-specific flags
    cmd.extend(get_platform_specific_flags())

    print("Build command:", " ".join(cmd))

    # Execute build
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Build failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def run_platform_script(target_os):
    """Run platform-specific build script."""
    system = platform.system().lower()

    if target_os == "macos":
        if system != "darwin":
            print("Error: macOS builds can only be created on macOS")
            return False
        script = "scripts/build_macos.sh"
        if not Path(script).exists():
            print("Error: macOS build script not found")
            return False
        # Make script executable and run
        subprocess.run(["chmod", "+x", script], check=True)
        return subprocess.run(["./" + script], shell=True).returncode == 0

    elif target_os == "windows":
        if system != "windows":
            print("Error: Windows builds can only be created on Windows")
            return False
        script = "scripts\\build_windows.bat"
        if not Path(script).exists():
            print("Error: Windows build script not found")
            return False
        return subprocess.run([script], shell=True).returncode == 0

    elif target_os == "linux":
        print("Linux build requires Docker container setup")
        print("Please use Docker-based build approach")
        return False

    else:
        print(f"Unsupported platform: {target_os}")
        return False


def build_all_platforms():
    """Build for all supported platforms."""
    success_count = 0
    platforms = ["macos", "windows", "linux"]

    for plat in platforms:
        print(f"\n--- Building for {plat.upper()} ---")
        if run_platform_script(plat):
            success_count += 1
        else:
            print(f"Failed to build for {plat}")

    print(f"\nBuild Results: {success_count}/{len(platforms)} platforms successful")
    return success_count > 0


def clean_build_artifacts():
    """Clean build artifacts."""
    dirs_to_clean = ["dist", "build"]
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Cleaned {dir_name} directory")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="VideoDub unified build script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Build for current platform
  python build.py --platform macos   # Build for specific platform
  python build.py --all              # Build for all platforms
  python build.py --clean            # Clean build artifacts
  python build.py --output myapp     # Custom output filename
        """,
    )

    parser.add_argument(
        "platform",
        nargs="?",
        default="current",
        choices=["current", "macos", "windows", "linux"],
        help="Target platform to build for",
    )

    parser.add_argument(
        "--all", action="store_true", help="Build for all supported platforms"
    )

    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")

    parser.add_argument("--output", help="Custom output filename (without extension)")

    args = parser.parse_args()

    # Handle clean option
    if args.clean:
        clean_build_artifacts()
        return 0

    # Handle build commands
    if args.all:
        success = build_all_platforms()
    elif args.platform == "current":
        # Build for current platform using Nuitka directly
        success = build_executable(args.output)
    else:
        # Build for specific platform
        success = run_platform_script(args.platform)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
