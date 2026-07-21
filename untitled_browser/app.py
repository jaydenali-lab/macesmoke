"""Untitled Browser main window and application entry point."""

import os
import sys

from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QStyle,
    QTabWidget,
    QToolBar,
    QToolButton,
)
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEngineView

from . import APP_NAME, __version__
from .navigation import to_url
from .start_page import START_PAGE_HTML, START_PAGE_TITLE

STYLE_SHEET = """
QToolBar { border: 0; padding: 4px 6px; spacing: 2px; }
QLineEdit {
    border: 1px solid palette(mid);
    border-radius: 14px;
    padding: 4px 14px;
    margin: 0 6px;
}
QLineEdit:focus { border-color: palette(highlight); }
QTabBar::tab { padding: 5px 10px; max-width: 220px; }
"""


class BrowserTab(QWebEngineView):
    """One page of web content. Knows how to open popups as new tabs."""

    def __init__(self, window: "BrowserWindow"):
        super().__init__()
        self._window = window

    def createWindow(self, _type):
        # target=_blank links and window.open() land in a new tab.
        return self._window.add_tab(background=False)

    def load_start_page(self):
        self.setHtml(START_PAGE_HTML, QUrl("about:blank"))


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 800)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setElideMode(Qt.TextElideMode.ElideRight)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self._current_tab_changed)
        self.setCentralWidget(self.tabs)

        new_tab_button = QToolButton()
        new_tab_button.setText("+")
        new_tab_button.setToolTip("New tab (Ctrl+T)")
        new_tab_button.clicked.connect(lambda: self.add_tab())
        self.tabs.setCornerWidget(new_tab_button, Qt.Corner.TopRightCorner)

        self._build_toolbar()
        self._build_shortcuts()

        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self._on_download_requested)

        self.add_tab()

    # ---- chrome -----------------------------------------------------------

    def _build_toolbar(self):
        style = self.style()
        toolbar = QToolBar("Navigation")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.back_action = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack), "Back", self
        )
        self.back_action.triggered.connect(lambda: self.current_tab().back())
        toolbar.addAction(self.back_action)

        self.forward_action = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward), "Forward", self
        )
        self.forward_action.triggered.connect(lambda: self.current_tab().forward())
        toolbar.addAction(self.forward_action)

        self.reload_action = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "Reload", self
        )
        self.reload_action.triggered.connect(lambda: self.current_tab().reload())
        toolbar.addAction(self.reload_action)

        self.stop_action = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_BrowserStop), "Stop", self
        )
        self.stop_action.triggered.connect(lambda: self.current_tab().stop())
        self.stop_action.setVisible(False)
        toolbar.addAction(self.stop_action)

        self.address = QLineEdit()
        self.address.setPlaceholderText("Search the web or enter an address")
        self.address.setClearButtonEnabled(True)
        self.address.returnPressed.connect(self._navigate_from_address)
        toolbar.addWidget(self.address)

    def _build_shortcuts(self):
        def action(text, shortcut, handler):
            act = QAction(text, self)
            act.setShortcut(QKeySequence(shortcut))
            act.triggered.connect(handler)
            self.addAction(act)

        action("New tab", "Ctrl+T", lambda: self.add_tab())
        action("Close tab", "Ctrl+W", lambda: self.close_tab(self.tabs.currentIndex()))
        action("Focus address bar", "Ctrl+L", self._focus_address)
        action("Reload", "Ctrl+R", lambda: self.current_tab().reload())
        action("Reload", "F5", lambda: self.current_tab().reload())
        action("Back", "Alt+Left", lambda: self.current_tab().back())
        action("Forward", "Alt+Right", lambda: self.current_tab().forward())
        action("Next tab", "Ctrl+Tab", lambda: self._cycle_tab(1))
        action("Previous tab", "Ctrl+Shift+Tab", lambda: self._cycle_tab(-1))
        action("Zoom in", "Ctrl+=", lambda: self._zoom(0.1))
        action("Zoom out", "Ctrl+-", lambda: self._zoom(-0.1))
        action("Reset zoom", "Ctrl+0", lambda: self.current_tab().setZoomFactor(1.0))
        action("Quit", "Ctrl+Q", self.close)

    # ---- tabs -------------------------------------------------------------

    def current_tab(self) -> BrowserTab:
        return self.tabs.currentWidget()

    def add_tab(self, url: "str | None" = None, background: bool = False) -> BrowserTab:
        tab = BrowserTab(self)
        index = self.tabs.addTab(tab, START_PAGE_TITLE)

        tab.titleChanged.connect(lambda title, t=tab: self._title_changed(t, title))
        tab.iconChanged.connect(lambda icon, t=tab: self._icon_changed(t, icon))
        tab.urlChanged.connect(lambda qurl, t=tab: self._url_changed(t, qurl))
        tab.loadStarted.connect(lambda t=tab: self._load_state_changed(t, True))
        tab.loadFinished.connect(lambda _ok, t=tab: self._load_state_changed(t, False))

        if url:
            tab.load(QUrl(url))
        else:
            tab.load_start_page()

        if not background:
            self.tabs.setCurrentIndex(index)
            if not url:
                self._focus_address()
        return tab

    def close_tab(self, index: int):
        tab = self.tabs.widget(index)
        if tab is None:
            return
        self.tabs.removeTab(index)
        tab.deleteLater()
        if self.tabs.count() == 0:
            self.add_tab()

    def _cycle_tab(self, step: int):
        count = self.tabs.count()
        if count:
            self.tabs.setCurrentIndex((self.tabs.currentIndex() + step) % count)

    # ---- signal handlers --------------------------------------------------

    def _current_tab_changed(self, _index: int):
        tab = self.current_tab()
        if tab is None:
            return
        self._refresh_address(tab)
        self._refresh_window_title(tab)
        self._refresh_nav_actions(tab)

    def _title_changed(self, tab: BrowserTab, title: str):
        index = self.tabs.indexOf(tab)
        if index != -1:
            self.tabs.setTabText(index, title or START_PAGE_TITLE)
        if tab is self.current_tab():
            self._refresh_window_title(tab)

    def _icon_changed(self, tab: BrowserTab, icon: QIcon):
        index = self.tabs.indexOf(tab)
        if index != -1:
            self.tabs.setTabIcon(index, icon)

    def _url_changed(self, tab: BrowserTab, _qurl: QUrl):
        if tab is self.current_tab():
            self._refresh_address(tab)
            self._refresh_nav_actions(tab)

    def _load_state_changed(self, tab: BrowserTab, loading: bool):
        if tab is self.current_tab():
            self.reload_action.setVisible(not loading)
            self.stop_action.setVisible(loading)
            self._refresh_nav_actions(tab)

    def _on_download_requested(self, download):
        download.accept()
        self.statusBar().showMessage(
            f"Downloading {download.downloadFileName()} to {download.downloadDirectory()}",
            8000,
        )

    # ---- helpers ----------------------------------------------------------

    def _navigate_from_address(self):
        url = to_url(self.address.text())
        tab = self.current_tab()
        if url and tab is not None:
            tab.load(QUrl(url))
            tab.setFocus()

    def _focus_address(self):
        self.address.setFocus()
        self.address.selectAll()

    def _refresh_address(self, tab: BrowserTab):
        if self.address.hasFocus():
            return
        url = tab.url().toString()
        self.address.setText("" if url == "about:blank" else url)

    def _refresh_window_title(self, tab: BrowserTab):
        title = tab.title()
        self.setWindowTitle(f"{title} — {APP_NAME}" if title else APP_NAME)

    def _refresh_nav_actions(self, tab: BrowserTab):
        history = tab.history()
        self.back_action.setEnabled(history.canGoBack())
        self.forward_action.setEnabled(history.canGoForward())


def main() -> int:
    QApplication.setApplicationName(APP_NAME)
    QApplication.setApplicationVersion(__version__)
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)

    window = BrowserWindow()
    for arg in sys.argv[1:]:
        if not arg.startswith("-"):
            window.add_tab(to_url(arg))
    window.show()

    # Used by CI to verify a packaged build starts up and shuts down cleanly.
    if os.environ.get("UNTITLED_BROWSER_SMOKE"):
        QTimer.singleShot(5000, app.quit)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
