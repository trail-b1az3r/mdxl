#!/usr/bin/env python3
"""CTE: QML desktop interface with a Python document and rendering backend."""
import html
import sys
from pathlib import Path

from PySide6.QtCore import (
    QAbstractListModel, QModelIndex, Property, QUrl, Qt, Signal, Slot,
)
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtQml import QQmlApplicationEngine

try:
    from PySide6.QtWebEngineQuick import QtWebEngineQuick
except ImportError as exc:
    raise SystemExit(
        "CTE requires the Qt WebEngine Quick module. Install qt6-webengine and pyside6."
    ) from exc

try:
    from mdxl_preview import render_mdxl
except ImportError as exc:
    raise SystemExit(
        "CTE needs the MDXL renderer. Install the Arch package dependencies."
    ) from exc

APP_NAME = "Concentrated Text Editor"
UNTITLED = "Untitled.mdxl"
ROLE_NAMES = {
    Qt.ItemDataRole.UserRole + 1: b"title",
    Qt.ItemDataRole.UserRole + 2: b"content",
    Qt.ItemDataRole.UserRole + 3: b"path",
    Qt.ItemDataRole.UserRole + 4: b"modified",
    Qt.ItemDataRole.UserRole + 5: b"words",
    Qt.ItemDataRole.UserRole + 6: b"characters",
}


class DocumentsModel(QAbstractListModel):
    """The tab model; every edit emits roles needed by QML, including live counts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._documents = []

    def roleNames(self):
        return ROLE_NAMES

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._documents)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._documents)):
            return None
        doc = self._documents[index.row()]
        content = doc["content"]
        if role == Qt.ItemDataRole.UserRole + 1:
            return doc["title"]
        if role == Qt.ItemDataRole.UserRole + 2:
            return content
        if role == Qt.ItemDataRole.UserRole + 3:
            return doc["path"]
        if role == Qt.ItemDataRole.UserRole + 4:
            return doc["modified"]
        if role == Qt.ItemDataRole.UserRole + 5:
            return len(content.split())
        if role == Qt.ItemDataRole.UserRole + 6:
            return len(content)
        if role == Qt.ItemDataRole.DisplayRole:
            return doc["title"]
        return None

    def document(self, row):
        if 0 <= row < len(self._documents):
            return self._documents[row]
        return None

    def add_document(self, path=None, content=""):
        path_value = str(Path(path).resolve()) if path else ""
        title = Path(path_value).name if path_value else UNTITLED
        row = len(self._documents)
        self.beginInsertRows(QModelIndex(), row, row)
        self._documents.append({
            "title": title,
            "content": content,
            "path": path_value,
            "modified": False,
        })
        self.endInsertRows()
        return row

    def update_content(self, row, content):
        doc = self.document(row)
        if doc is None or doc["content"] == content:
            return False
        doc["content"] = content
        doc["modified"] = True
        idx = self.index(row, 0)
        self.dataChanged.emit(idx, idx, [
            Qt.ItemDataRole.UserRole + 2,
            Qt.ItemDataRole.UserRole + 4,
            Qt.ItemDataRole.UserRole + 5,
            Qt.ItemDataRole.UserRole + 6,
        ])
        return True

    def set_path_and_saved(self, row, path):
        doc = self.document(row)
        if doc is None:
            return
        resolved = str(Path(path).resolve())
        doc["path"] = resolved
        doc["title"] = Path(resolved).name
        doc["modified"] = False
        idx = self.index(row, 0)
        self.dataChanged.emit(idx, idx, [
            Qt.ItemDataRole.UserRole + 1,
            Qt.ItemDataRole.UserRole + 3,
            Qt.ItemDataRole.UserRole + 4,
        ])

    def remove_document(self, row):
        if not (0 <= row < len(self._documents)):
            return
        self.beginRemoveRows(QModelIndex(), row, row)
        self._documents.pop(row)
        self.endRemoveRows()


class CTEBackend:
    """Python QObject exposed to QML; owns file operations, counts, fonts and HTML."""

    from PySide6.QtCore import QObject

    currentIndexChanged = Signal()
    currentDocumentChanged = Signal()
    fontFamilyChanged = Signal()
    previewChanged = Signal()
    statusChanged = Signal()
    modeChanged = Signal()
    countsChanged = Signal()

    def __init__(self, app, initial_files=()):
        self._app = app
        self._documents = DocumentsModel()
        self._current_index = -1
        self._mode = "edit"
        self._status = "Ready"
        self._font_families = sorted(QFontDatabase.families())
        if not self._font_families:
            self._font_families = ["Sans Serif"]
        preferred = "Noto Sans"
        self._font_family = preferred if preferred in self._font_families else self._font_families[0]
        self._rendered_html = ""
        self._base_url = QUrl.fromLocalFile(str(Path.home()) + "/")
        for filename in initial_files:
            self._open_file(filename, report_errors=True)
        if self._documents.rowCount() == 0:
            self._documents.add_document()
        if self._current_index < 0:
            self._current_index = 0
        self._refresh_preview()

    def _current_doc(self):
        return self._documents.document(self._current_index)

    def _set_status(self, message):
        if self._status != message:
            self._status = message
            self.statusChanged.emit()

    def _render(self, source, path_value):
        page = render_mdxl(source, live=False)
        family = self._font_family.replace("\\", "\\\\").replace('"', '\\"')
        font_css = (
            "<style id=\"cte-font-overrides\">"
            "body, article, article p, article h1, article h2, article h3, article h4, "
            "article h5, article h6, article li, article blockquote, article table, "
            "article th, article td, article button, article label { "
            "font-family: \"" + family + "\", sans-serif !important; }"
            "pre, pre *, code, code * { font-family: ui-monospace, monospace !important; }"
            "</style>"
        )
        page = page.replace("</head>", font_css + "</head>", 1)
        return page

    def _refresh_preview(self):
        doc = self._current_doc()
        if doc and doc["path"]:
            parent = str(Path(doc["path"]).parent) + "/"
        else:
            parent = str(Path.home()) + "/"
        self._base_url = QUrl.fromLocalFile(parent)
        source = doc["content"] if doc else ""
        self._rendered_html = self._render(source, doc["path"] if doc else "")
        self.previewChanged.emit()

    def _set_current_index(self, index):
        count = self._documents.rowCount()
        if count == 0:
            index = -1
        else:
            index = max(0, min(int(index), count - 1))
        if self._current_index == index:
            return
        self._current_index = index
        self.currentIndexChanged.emit()
        self.currentDocumentChanged.emit()
        self.countsChanged.emit()
        self._refresh_preview()

    def get_documents(self):
        return self._documents

    def get_current_index(self):
        return self._current_index

    def get_current_content(self):
        doc = self._current_doc()
        return doc["content"] if doc else ""

    def get_font_families(self):
        return self._font_families

    def get_font_family(self):
        return self._font_family

    def set_font_family(self, family):
        family = str(family)
        if family not in self._font_families or family == self._font_family:
            return
        self._font_family = family
        self._app.setFont(QFont(family, 10))
        self.fontFamilyChanged.emit()
        self._refresh_preview()

    def get_word_count(self):
        return len(self.get_current_content().split())

    def get_character_count(self):
        return len(self.get_current_content())

    def get_status(self):
        return self._status

    def get_mode(self):
        return self._mode

    def get_rendered_html(self):
        return self._rendered_html

    def get_base_url(self):
        return self._base_url

    documents = Property("QVariant", get_documents, constant=True)
    currentIndex = Property(int, get_current_index, notify=currentIndexChanged)
    currentContent = Property(str, get_current_content, notify=currentDocumentChanged)
    fontFamilies = Property("QStringList", get_font_families, constant=True)
    fontFamily = Property(str, get_font_family, set_font_family, notify=fontFamilyChanged)
    wordCount = Property(int, get_word_count, notify=countsChanged)
    characterCount = Property(int, get_character_count, notify=countsChanged)
    status = Property(str, get_status, notify=statusChanged)
    mode = Property(str, get_mode, notify=modeChanged)
    renderedHtml = Property(str, get_rendered_html, notify=previewChanged)
    baseUrl = Property(QUrl, get_base_url, notify=previewChanged)

    @Slot(int)
    def setCurrentIndex(self, index):
        self._set_current_index(index)

    @Slot(str)
    def setMode(self, mode):
        if mode not in {"edit", "render"} or mode == self._mode:
            return
        self._mode = mode
        self.modeChanged.emit()
        self._set_status("Edit mode" if mode == "edit" else "Rendered MDXL")

    @Slot(str)
    def setFontFamily(self, family):
        self.set_font_family(family)

    @Slot(str)
    def updateContent(self, content):
        doc = self._current_doc()
        if not doc or not self._documents.update_content(self._current_index, content):
            return
        self.currentDocumentChanged.emit()
        self.countsChanged.emit()
        self._refresh_preview()
        self._set_status("Unsaved changes")

    @Slot(int, result=str)
    def contentAt(self, index):
        doc = self._documents.document(index)
        return doc["content"] if doc else ""

    @Slot()
    def newDocument(self):
        row = self._documents.add_document()
        self._set_current_index(row)
        self._set_status("New MDXL page")

    @Slot()
    def openDialog(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            None, "Open MDXL documents", str(Path.home()),
            "MDXL and Markdown (*.mdxl *.md *.markdown *.mdown *.txt);;All files (*)",
        )
        for filename in filenames:
            self._open_file(filename, report_errors=True)

    def _open_file(self, filename, report_errors=True):
        path = Path(filename).expanduser().resolve()
        for row in range(self._documents.rowCount()):
            doc = self._documents.document(row)
            if doc and doc["path"] == str(path):
                self._set_current_index(row)
                return
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            if report_errors:
                QMessageBox.warning(None, "Could not open document", str(exc))
            return
        row = self._documents.add_document(path, content)
        self._set_current_index(row)
        self._set_status("Opened " + path.name)

    @Slot()
    def saveCurrent(self):
        self._save_document(self._current_index, save_as=False)

    @Slot()
    def saveAsCurrent(self):
        self._save_document(self._current_index, save_as=True)

    def _save_document(self, row, save_as=False):
        doc = self._documents.document(row)
        if not doc:
            return False
        filename = doc["path"]
        if not filename or save_as:
            filename, _ = QFileDialog.getSaveFileName(
                None, "Save MDXL document",
                filename or str(Path.home() / UNTITLED),
                "MDXL documents (*.mdxl);;Markdown documents (*.md);;All files (*)",
            )
            if not filename:
                return False
        try:
            Path(filename).expanduser().resolve().write_text(doc["content"], encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(None, "Could not save document", str(exc))
            return False
        self._documents.set_path_and_saved(row, filename)
        if row == self._current_index:
            self._refresh_preview()
        self._set_status("Saved " + Path(filename).name)
        return True

    @Slot(int)
    def closeDocument(self, row):
        doc = self._documents.document(row)
        if not doc:
            return
        if doc["modified"]:
            choice = QMessageBox.question(
                None, "Unsaved changes",
                "Save changes to " + doc["title"] + " before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if choice == QMessageBox.StandardButton.Cancel:
                return
            if choice == QMessageBox.StandardButton.Save and not self._save_document(row):
                return
        self._documents.remove_document(row)
        if self._documents.rowCount() == 0:
            row = self._documents.add_document()
            self._current_index = row
            self.currentIndexChanged.emit()
            self.currentDocumentChanged.emit()
            self.countsChanged.emit()
            self._refresh_preview()
        else:
            next_index = self._current_index
            if row < next_index:
                next_index -= 1
            elif row == next_index:
                next_index = min(row, self._documents.rowCount() - 1)
            self._current_index = -1
            self._set_current_index(next_index)
        self._set_status("Page closed")

    @Slot(result=bool)
    def confirmCloseAll(self):
        for row in range(self._documents.rowCount()):
            doc = self._documents.document(row)
            if not doc or not doc["modified"]:
                continue
            self._set_current_index(row)
            choice = QMessageBox.question(
                None, "Unsaved changes",
                "Save changes to " + doc["title"] + " before exiting?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if choice == QMessageBox.StandardButton.Cancel:
                return False
            if choice == QMessageBox.StandardButton.Save and not self._save_document(row):
                return False
        return True


def main():
    # Qt WebEngine initialization must happen before the Qt application is created.
    QtWebEngineQuick.initialize()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("MDXL")
    app.setFont(QFont("Noto Sans", 10))

    backend = CTEBackend(app, sys.argv[1:])
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", backend)
    qml_file = Path(__file__).with_name("main.qml")
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
