import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIME_NS = {"mime": "http://www.freedesktop.org/standards/shared-mime-info"}


class KateAndMimeTests(unittest.TestCase):
    def test_kate_language_is_named_and_registered_for_mdxl(self):
        root = ET.parse(ROOT / "mdxl.xml").getroot()
        self.assertEqual(root.tag, "language")
        self.assertEqual(root.get("name"), "Markdown Extended Logic")
        self.assertEqual(root.get("mimetype"), "text/x-mdxl")
        self.assertIn("*.mdxl", root.get("extensions", "").split(";"))
        self.assertEqual(root.get("priority"), "100")

    def test_kate_definition_imports_standard_markdown_highlighting(self):
        root = ET.parse(ROOT / "mdxl.xml").getroot()
        includes = [
            element for element in root.findall(".//IncludeRules")
            if element.get("context") == "Normal Text##Markdown"
        ]
        self.assertTrue(includes, "MDXL should reuse Kate's built-in Markdown grammar")
        self.assertEqual(includes[0].get("includeAttrib"), "true")
        attribute_rule = next(
            rule for rule in root.findall(".//RegExpr")
            if rule.get("attribute") == "HeadingAttributes"
        )
        self.assertIn(r"\.[A-Za-z0-9_-]+", attribute_rule.get("String", ""))
        self.assertIn('"', attribute_rule.get("String", ""))

        attributes = {
            element.get("attribute")
            for element in root.findall(".//contexts/*/*")
            if element.get("attribute")
        }
        expected = {
            "MicroHeader1", "MicroHeader2", "MicroHeader3", "AlertMarker",            "PlusHeader1", "PlusHeader2", "DoubleBlockquote", "StripedThrough",
            "TaskList", "FootnoteDefinition", "Abbreviation", "Details",
            "DefinitionList", "TableDelimiter", "HeadingAttributes", "Footnote",
            "Inserted", "Superscript", "Mark", "Strikethrough", "AutoLink",
            "Special", "Arrow", "InvisibleInk", "ColorTag", "HighlightTag",
            "RedactTag", "RainbowTag", "KeyTag", "ProgressBar",
        }
        self.assertTrue(expected.issubset(attributes), f"Missing highlight rules: {expected - attributes}")

    def test_mime_package_names_the_file_type(self):
        root = ET.parse(ROOT / "data" / "mime" / "packages" / "mdxl.xml").getroot()
        mime_type = root.find("mime:mime-type[@type='text/x-mdxl']", MIME_NS)
        self.assertIsNotNone(mime_type)
        self.assertEqual(mime_type.findtext("mime:comment", namespaces=MIME_NS), "Markdown Extended Logic document")
        self.assertEqual(mime_type.find("mime:sub-class-of", MIME_NS).get("type"), "text/markdown")
        self.assertEqual(mime_type.find("mime:glob", MIME_NS).get("pattern"), "*.mdxl")

    def test_installer_registers_the_syntax_and_refreshes_mime_database(self):
        installer = (ROOT / "install.sh").read_text(encoding="utf-8")
        self.assertIn('install -m 644 "$SCRIPT_DIR/mdxl.xml" "$KATE_DIR/mdxl.xml"', installer)
        self.assertIn('install -m 644 "$SCRIPT_DIR/data/mime/packages/mdxl.xml" "$MIME_PACKAGE_DIR/mdxl.xml"', installer)
        self.assertIn('update-mime-database "$HOME/.local/share/mime"', installer)
        self.assertIn("Markdown Extended Logic document", installer)


if __name__ == "__main__":
    unittest.main()
