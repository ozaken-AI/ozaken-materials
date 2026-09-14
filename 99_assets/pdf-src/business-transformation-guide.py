#!/usr/bin/env python3
"""Compatibility entry point for the current public business PDF.

Content: beginner_guides/business.json
Layout and build: beginner_guides/build.py
The former HTML generator is preserved in Git history through 7729bf4.
"""
from pathlib import Path
import runpy
import sys

if __name__ == '__main__':
    if '--only' in sys.argv:
        raise SystemExit('This entry point builds only the business guide; use beginner_guides/build.py for others')
    sys.argv += ['--only', 'business']
    runpy.run_path(str(Path(__file__).parent / 'beginner_guides' / 'build.py'), run_name='__main__')
