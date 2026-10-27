import unittest

from mdxl_cli import render_terminal


class TerminalRendererTests(unittest.TestCase):
    def test_micro_and_subheadings_are_styled(self):
        rendered = render_terminal("-# one\n-## two\n-### three\n#### four")
        for word in ("one", "two", "three", "four"):
            self.assertIn(word, rendered)
        self.assertIn("\033[1;96m", rendered)

    def test_color_rainbow_and_highlight(self):
        rendered = render_terminal("/col//green /col#00FF00// /rbw//rgb// //hl//notice//hl//")
        self.assertIn("\033[38;2;0;255;0m", rendered)
        self.assertIn("\033[38;2;", rendered)
        self.assertIn("\033[43;30mnotice", rendered)

    def test_progress_clamps_to_one_hundred(self):
        self.assertIn("100%", render_terminal("/bar//999//"))
        self.assertIn("0%", render_terminal("/bar//0//"))

    def test_arrows_and_shortcode(self):
        rendered = render_terminal("[[==>>]] [[<<==]] [[<=>>]] :check:")
        for symbol in ("➜", "⬅", "⇄", "✅"):
            self.assertIn(symbol, rendered)


if __name__ == "__main__":
    unittest.main()
