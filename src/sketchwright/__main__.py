"""Module execution entry point for python -m sketchwright."""

import sys

from sketchwright.cli import main

if __name__ == "__main__":
    main(sys.argv[1:])
