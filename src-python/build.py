#!/usr/bin/env python3
"""Build script for creating the anonymize-api binary."""

import platform
import subprocess
import sys
from pathlib import Path


def get_binary_name() -> str:
    """Get the appropriate binary name for the current platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        if machine == "arm64":
            return "anonymize-api-aarch64-apple-darwin"
        return "anonymize-api-x86_64-apple-darwin"
    elif system == "windows":
        return "anonymize-api-x86_64-pc-windows-msvc.exe"
    elif system == "linux":
        if machine == "aarch64":
            return "anonymize-api-aarch64-unknown-linux-gnu"
        return "anonymize-api-x86_64-unknown-linux-gnu"
    else:
        return f"anonymize-api-{machine}-{system}"


def main():
    """Build the binary using PyInstaller."""
    src_python = Path(__file__).parent
    project_root = src_python.parent
    output_dir = project_root / "src-tauri" / "binaries"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    binary_name = get_binary_name()
    print(f"Building binary: {binary_name}")

    # Find spaCy model location
    import spacy
    model_path = Path(spacy.util.get_package_path("de_core_news_sm"))

    # Path separator for --add-data is different on Windows
    path_sep = ";" if platform.system() == "Windows" else ":"

    # PyInstaller command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        binary_name.replace(".exe", ""),
        "--distpath",
        str(output_dir),
        "--workpath",
        str(src_python / "build"),
        "--specpath",
        str(src_python),
        # Include spaCy model data
        "--add-data",
        f"{model_path}{path_sep}de_core_news_sm",
        # Hidden imports that PyInstaller might miss
        "--hidden-import",
        "uvicorn.logging",
        "--hidden-import",
        "uvicorn.loops",
        "--hidden-import",
        "uvicorn.loops.auto",
        "--hidden-import",
        "uvicorn.protocols",
        "--hidden-import",
        "uvicorn.protocols.http",
        "--hidden-import",
        "uvicorn.protocols.http.auto",
        "--hidden-import",
        "uvicorn.protocols.websockets",
        "--hidden-import",
        "uvicorn.protocols.websockets.auto",
        "--hidden-import",
        "uvicorn.lifespan",
        "--hidden-import",
        "uvicorn.lifespan.on",
        "--hidden-import",
        "presidio_analyzer",
        "--hidden-import",
        "presidio_anonymizer",
        "--hidden-import",
        "spacy",
        "--hidden-import",
        "de_core_news_sm",
        "--hidden-import",
        "thinc.backends.numpy_ops",
        "--collect-all",
        "presidio_analyzer",
        "--collect-all",
        "presidio_anonymizer",
        "--collect-all",
        "spacy",
        "--collect-all",
        "de_core_news_sm",
        "--collect-all",
        "thinc",
        # Entry point
        str(src_python / "anonymize_api" / "main.py"),
    ]

    print("Running PyInstaller...")
    result = subprocess.run(cmd, cwd=src_python)

    if result.returncode == 0:
        print(f"\nBinary built successfully: {output_dir / binary_name}")
    else:
        print(f"\nBuild failed with exit code: {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
