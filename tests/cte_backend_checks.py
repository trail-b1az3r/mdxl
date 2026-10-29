import os
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtWidgets import QApplication

from cte.cte import CTEBackend


class CTEBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.backend = CTEBackend(self.app)

    def test_live_word_and_character_counts(self):
        self.assertEqual(self.backend.wordCount, 0)
        self.assertEqual(self.backend.characterCount, 0)

        source = "first second\nthird"
        self.backend.updateContent(source)

        self.assertEqual(self.backend.wordCount, 3)
        self.assertEqual(self.backend.characterCount, len(source))
        self.assertTrue(self.backend.documents.document(0)["modified"])

    def test_selected_installed_font_is_in_rendered_html(self):
        families = self.backend.fontFamilies
        self.assertGreater(len(families), 0)
        target = families[-1]
        self.backend.setFontFamily(target)

        self.assertEqual(self.backend.fontFamily, target)
        self.assertIn(
            'font-family: "' + target.replace("\\", "\\\\").replace('"', '\\"') + '", sans-serif !important;',
            self.backend.renderedHtml,
        )

    def test_switching_document_refreshes_counts_and_preview(self):
        self.backend.updateContent("one two")
        self.backend.newDocument()
        self.assertEqual(self.backend.wordCount, 0)
        self.backend.updateContent("# Second page\n\nnew text")
        self.assertEqual(self.backend.wordCount, 5)
        self.assertIn("<h1", self.backend.renderedHtml)
        self.assertIn("new text", self.backend.renderedHtml)

    def test_qml_interface_and_webengine_are_packaged(self):
        qml_path = Path(__file__).resolve().parents[1] / "cte" / "main.qml"
        self.assertTrue(qml_path.is_file())
        qml = qml_path.read_text(encoding="utf-8")
        self.assertIn("import QtWebEngine", qml)
        self.assertIn("backend.wordCount", qml)
        self.assertIn("backend.fontFamily", qml)
        self.assertIn("onTextChanged", qml)
        self.assertIn("preview.loadHtml(backend.renderedHtml, backend.baseUrl)", qml)

        engine = QQmlEngine()
        component = QQmlComponent(engine, QUrl.fromLocalFile(str(qml_path)))
        errors = "\\n".join(error.toString() for error in component.errors())
        self.assertTrue(component.isReady(), errors)


if __name__ == "__main__":
    unittest.main()
