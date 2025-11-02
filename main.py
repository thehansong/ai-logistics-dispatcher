#!/usr/bin/env python3
"""
Smart Delivery Allocator - Main Entry Point
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from allocator import main

if __name__ == "__main__":
    main()