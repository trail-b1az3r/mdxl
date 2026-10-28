#!/usr/bin/env python3
"""CTE — Concentrated Text Editor, a native MDXL editor for Linux."""
import html
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QAction, QFont, QFontDatabase, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QPushButton, QSplitter, QTabWidget,
    QTextEdit, QVBoxLayout, QWidget, QStatusBar
)
from PySide6.QtWebEngineWidgets import QWebEngineView

try:
    from mdxl_preview import render_mdxl
except ImportError as exc:
    raise SystemExit("CTE needs the MDXL renderer. Install the Arch package dependencies.") from exc

APP_NAME = "Concentrated Text Editor"
UNTITLED = "Untitled.mdxl"

APP_STYLE = """
QWidget { background: #111411; color: #e5e9df; font-size: 14px; }
QMainWindow { background: #111411; }
QFrame#TopBar, QFrame#ToolBar, QFrame#BottomBar { background: #1b201b; border: 1px solid #30382e; border-radius: 22px; }
QLabel#Brand { color: #d5f6a0; font-size: 21px; font-weight: 700; padding: 3px 8px; }
QLabel#SubBrand { color: #a6b29e; font-size: 11px; }
QPushButton { background: #252d24; border: 1px solid #3b4637; border-radius: 17px; padding: 10px 16px; color: #e5e9df; font-weight: 600; }
QPushButton:hover { background: #303c2c; border-color: #91b96b; }
QPushButton:checked, QPushButton#Primary { background: #d5f6a0; color: #1d2915; border-color: #d5f6a0; }
QPushButton#IconButton { min-width: 28px; max-width: 28px; padding: 8px; border-radius: 14px; }
QComboBox { background: #252d24; border: 1px solid #3b4637; border-radius: 14px; padding: 8px 12px; min-width: 130px; }
QComboBox QAbstractItemView { background: #20271f; selection-background-color: #d5f6a0; selection-color: #1d2915; }
QTabWidget::pane { border: 1px solid #30382e; border-radius: 18px; top: -1px; background: #151915; }
QTabBar::tab { background: #20251f; color: #b7c0b0; padding: 12px 18px; margin: 4px 3px 0 3px; border-radius: 13px; }
QTabBar::tab:selected { background: #d5f6a0; color: #1d2915; font-weight: 700; }
QTextEdit { background: #151915; color: #e5e9df; border: 0; padding: 22px; selection-background-color: #48663a; font-size: 15px; }
QStatusBar { background: #111411; color: #9eaa97; }
QSplitter::handle { background: #30382e; width: 2px; }
"""

RENDER_CSS = """
<style>
:root{color-scheme:dark;--bg:#151915;--panel:#20271f;--text:#e5e9df;--muted:#a6b29e;--accent:#d5f6a0;--line:#3b4637}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(60rem 32rem at 80% -15%,#2c3d25 0%,transparent 60%),var(--bg);background-repeat:no-repeat;color:var(--text);font:16px/1.75 sans-serif}
article{max-width:920px;margin:auto;padding:clamp(24px,5vw,64px)}h1,h2,h3,h4{line-height:1.2;letter-spacing:-.025em}h1{font-size:2.5rem}h2{margin-top:2.3em}a{color:#b4dbff}pre,code{font-family:monospace}pre{padding:18px;border-radius:18px;background:#0e110e;overflow:auto}blockquote{margin-left:0;padding:4px 20px;border-left:4px solid var(--accent);color:#c6d1bd}table{border-collapse:collapse;width:100%;display:block;overflow:auto}th,td{border:1px solid var(--line);padding:8px 12px}th{background:var(--panel)}hr{border:0;border-top:1px solid var(--line)}mark{background:#e6b86b;color:#251d10}del{text-decoration:line-through;color:#aab0a5}ins{background:#284a31} .task-list-item{list-style:none}.exec-block{border:1px solid var(--line);border-radius:18px;overflow:hidden;margin:20px 0}.exec-header{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:var(--panel)}.exec-actions{display:flex;gap:8px}.exec-actions button{border:1px solid var(--line);border-radius:12px;padding:7px 11px;background:#303c2c;color:var(--text)}.exec-block pre{margin:0;border-radius:0}.exec-output{padding:10px 14px}.document-format{padding:36px;background:#f7f4ec;color:#242821;border-radius:4px;box-shadow:0 14px 45px #0004;font-family:Georgia,serif}.document-format h1,.document-format h2{color:#242821}
</style>
"""

class DocumentPage(QWidget):
    def __init__(self, path=None, content=""):
        super().__init__()
        self.path = Path(path).resolve() if path else None
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.editor.setPlainText(content)
        self.preview = QWebEngineView()
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.preview)
        self.splitter.setSizes([560, 560])
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)
        self.editor.textChanged.connect(self._changed)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self.render)
        self.render()
    def _changed(self):
        self._timer.start()
        window = self.window()
        if isinstance(window, CTEWindow):
            window.update_tab_title(self)
    def render(self):
        source = self.editor.toPlainText()
        try:
            page = render_mdxl(source, live=False)
            # Keep the renderer's security policy and behavior, then apply CTE's theme.
            page = page.replace("</head>", RENDER_CSS + "</head>", 1)
            self.preview.setHtml(page, QUrl.fromLocalFile(str(self.path.parent if self.path else Path.home()) + "/"))
        except Exception as exc:
            self.preview.setHtml("<html><body style='background:#151915;color:#ffb4ab;font:14px monospace;padding:24px'>Render error: " + html.escape(str(exc)) + "</body></html>")
    def save(self, save_as=False):
        if self.path is None or save_as:
            filename, _ = QFileDialog.getSaveFileName(self, "Save MDXL document", str(self.path or Path.home() / UNTITLED), "MDXL documents (*.mdxl);;Markdown documents (*.md);;All files (*)")
            if not filename:
                return False
            self.path = Path(filename).resolve()
        try:
            self.path.write_text(self.editor.toPlainText(), encoding="utf-8")
            self.editor.document().setModified(False)
            return True
        except OSError as exc:
            QMessageBox.critical(self, "Could not save document", str(exc))
            return False

class CTEWindow(QMainWindow):
    def __init__(self, initial_files=()):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1440, 920)
        self.setMinimumSize(920, 620)
        self.mode = "edit"
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(18, 16, 18, 12)
        root_layout.setSpacing(12)
        top = QFrame(objectName="TopBar")
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(18, 12, 18, 12)
        brand_col = QVBoxLayout()
        brand = QLabel("CTE", objectName="Brand")
        subtitle = QLabel("Concentrated Text Editor  ·  MDXL workspace", objectName="SubBrand")
        brand_col.addWidget(brand)
        brand_col.addWidget(subtitle)
        top_layout.addLayout(brand_col)
        top_layout.addStretch()
        self.mode_edit = QPushButton("Edit")
        self.mode_render = QPushButton("Render")
        self.mode_edit.setCheckable(True)
        self.mode_render.setCheckable(True)
        self.mode_edit.setChecked(True)
        self.mode_edit.clicked.connect(lambda: self.set_mode("edit"))
        self.mode_render.clicked.connect(lambda: self.set_mode("render"))
        top_layout.addWidget(self.mode_edit)
        top_layout.addWidget(self.mode_render)
        root_layout.addWidget(top)
        toolbar = QFrame(objectName="ToolBar")
        tools = QHBoxLayout(toolbar)
        tools.setContentsMargins(14, 9, 14, 9)
        self.new_btn = QPushButton("New page")
        self.open_btn = QPushButton("Open")
        self.save_btn = QPushButton("Save")
        self.fonts = QComboBox()
        self.fonts.setToolTip("Choose an installed system font")
        self.fonts.addItems(sorted(QFontDatabase.families()))
        default_font = QApplication.font().family()
        if self.fonts.findText(default_font) >= 0:
            self.fonts.setCurrentText(default_font)
        self.fonts.currentTextChanged.connect(self.change_font)
        tools.addWidget(self.new_btn)
        tools.addWidget(self.open_btn)
        tools.addWidget(self.save_btn)
        tools.addStretch()
        tools.addWidget(QLabel("Editor font"))
        tools.addWidget(self.fonts)
        root_layout.addWidget(toolbar)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self._tab_changed)
        root_layout.addWidget(self.tabs, 1)
        bottom = QFrame(objectName="BottomBar")
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(16, 8, 16, 8)
        self.status_label = QLabel("Ready")
        self.count_label = QLabel("0 words · 0 characters")
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.count_label)
        root_layout.addWidget(bottom)
        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())
        self.new_btn.clicked.connect(self.new_page)
        self.open_btn.clicked.connect(self.open_dialog)
        self.save_btn.clicked.connect(self.save_current)
        self._create_actions()
        if initial_files:
            for item in initial_files:
                self.open_file(item)
        if self.tabs.count() == 0:
            self.new_page()
        self.set_mode("edit")
        self.tabs.currentChanged.connect(lambda _: self.refresh_counts())
    def _create_actions(self):
        for label, shortcut, callback in [
            ("New page", QKeySequence.StandardKey.New, self.new_page),
            ("Open", QKeySequence.StandardKey.Open, self.open_dialog),
            ("Save", QKeySequence.StandardKey.Save, self.save_current),
            ("Save As", QKeySequence.StandardKey.SaveAs, lambda: self.current_page() and self.current_page().save(True)),
        ]:
            action = QAction(label, self)
            action.setShortcut(shortcut)
            action.triggered.connect(callback)
            self.addAction(action)
    def current_page(self):
        page = self.tabs.currentWidget()
        return page if isinstance(page, DocumentPage) else None
    def new_page(self):
        page = DocumentPage()
        index = self.tabs.addTab(page, UNTITLED)
        self.tabs.setCurrentIndex(index)
        self.status_label.setText("New MDXL page")
        self.refresh_counts()
    def open_dialog(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, "Open MDXL documents", str(Path.home()), "MDXL and Markdown (*.mdxl *.md *.markdown *.mdown *.txt);;All files (*)")
        for filename in filenames:
            self.open_file(filename)
    def open_file(self, filename):
        path = Path(filename).expanduser().resolve()
        for i in range(self.tabs.count()):
            existing = self.tabs.widget(i)
            if existing.path == path:
                self.tabs.setCurrentIndex(i)
                return
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            QMessageBox.warning(self, "Could not open document", str(exc))
            return
        page = DocumentPage(path, content)
        index = self.tabs.addTab(page, path.name)
        self.tabs.setCurrentIndex(index)
        self.update_tab_title(page)
        self.status_label.setText("Opened " + path.name)
    def save_current(self):
        page = self.current_page()
        if page and page.save():
            self.update_tab_title(page)
            self.status_label.setText("Saved " + (page.path.name if page.path else "document"))
    def close_tab(self, index):
        page = self.tabs.widget(index)
        if page.editor.document().isModified():
            choice = QMessageBox.question(self, "Unsaved changes", "Save changes before closing this page?", QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Save)
            if choice == QMessageBox.StandardButton.Cancel:
                return
            if choice == QMessageBox.StandardButton.Save and not page.save():
                return
        self.tabs.removeTab(index)
        page.deleteLater()
        if self.tabs.count() == 0:
            self.new_page()
    def update_tab_title(self, page):
        index = self.tabs.indexOf(page)
        if index < 0:
            return
        title = page.path.name if page.path else UNTITLED
        if page.editor.document().isModified():
            title = "• " + title
        self.tabs.setTabText(index, title)
    def set_mode(self, mode):
        self.mode = mode
        self.mode_edit.setChecked(mode == "edit")
        self.mode_render.setChecked(mode == "render")
        for i in range(self.tabs.count()):
            page = self.tabs.widget(i)
            page.editor.setVisible(mode == "edit")
            page.preview.setVisible(mode == "render")
            if mode == "render":
                page.render()
        self.status_label.setText("Edit mode" if mode == "edit" else "Rendered MDXL")
    def _tab_changed(self, _index):
        self.set_mode(self.mode)
        self.refresh_counts()
    def change_font(self, family):
        for i in range(self.tabs.count()):
            page = self.tabs.widget(i)
            font = page.editor.font()
            font.setFamily(family)
            page.editor.setFont(font)
    def refresh_counts(self):
        page = self.current_page()
        if not page:
            self.count_label.setText("0 words · 0 characters")
            return
        text = page.editor.toPlainText()
        self.count_label.setText(f"{len(text.split())} words · {len(text)} characters")
    def closeEvent(self, event):
        for i in range(self.tabs.count()):
            page = self.tabs.widget(i)
            if page.editor.document().isModified():
                self.tabs.setCurrentIndex(i)
                choice = QMessageBox.question(self, "Unsaved changes", f"Save changes to {self.tabs.tabText(i).lstrip('• ')}?", QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Save)
                if choice == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return
                if choice == QMessageBox.StandardButton.Save and not page.save():
                    event.ignore()
                    return
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("MDXL")
    app.setStyle("Fusion")
    app.setFont(QFont("Noto Sans", 10))
    app.setStyleSheet(APP_STYLE)
    window = CTEWindow(sys.argv[1:])
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
