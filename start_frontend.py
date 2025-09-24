#!/usr/bin/env python3
"""Script to start the Streamlit frontend."""

import subprocess
import sys

if __name__ == "__main__":
    print("Starting Streamlit frontend on http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend.py"])