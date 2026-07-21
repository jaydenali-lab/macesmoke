# Untitled Browser

A minimal tabbed web browser written in Python, powered by Qt WebEngine
(the same Chromium engine used by real browsers).

## Features

- Tabbed browsing: open, close, reorder, and cycle through tabs
- Smart address bar: URLs load directly, anything else becomes a DuckDuckGo search
- Back / forward / reload / stop navigation with live tab titles and favicons
- Popups and `target="_blank"` links open in new tabs
- File downloads (saved to your default download directory)
- Per-tab zoom and a built-in dark start page

## Getting started

Requires Python 3.9+.

```bash
pip install .
untitled-browser
```

Or run straight from a checkout:

```bash
pip install -r requirements.txt
python -m untitled_browser
```

You can also pass URLs on the command line: `untitled-browser example.com`.

## Windows executable

The **Build Windows exe** GitHub Actions workflow packages the browser into a
standalone `UntitledBrowser.exe` with PyInstaller and attaches it to a GitHub
release (no Python install needed to run it). To build locally on a Windows
machine instead:

```bash
pip install . pyinstaller
pyinstaller --noconfirm --onefile --windowed --name UntitledBrowser launcher.py
```

The executable lands in `dist\UntitledBrowser.exe`.

## Keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl+T` | New tab |
| `Ctrl+W` | Close tab |
| `Ctrl+L` | Focus the address bar |
| `Ctrl+R` / `F5` | Reload |
| `Alt+Left` / `Alt+Right` | Back / forward |
| `Ctrl+Tab` / `Ctrl+Shift+Tab` | Next / previous tab |
| `Ctrl+=` / `Ctrl+-` / `Ctrl+0` | Zoom in / out / reset |
| `Ctrl+Q` | Quit |

On macOS, use `Cmd` in place of `Ctrl`.

## Project layout

```
untitled_browser/
├── app.py         # main window, tabs, toolbar, shortcuts
├── navigation.py  # address-bar input → URL (or search) logic
├── start_page.py  # the built-in new-tab page
└── __main__.py    # `python -m untitled_browser` entry point
tests/
└── test_navigation.py
```

## Tests

The URL-handling logic is plain Python and tested without Qt:

```bash
pip install pytest
pytest
```
