"""PyInstaller entry point (see .github/workflows/build-windows.yml)."""

import sys

from untitled_browser.app import main

if __name__ == "__main__":
    sys.exit(main())
