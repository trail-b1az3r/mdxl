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

    def test_five_backtick_code_keeps_markdown_tokens_literal(self):
        source = "`````python\nprint('~~not strike~~ /rbw//not rainbow//rbw//')\n`````"
        rendered = render_terminal(source)
        self.assertIn("~~not strike~~", rendered)
        self.assertIn("/rbw//not rainbow//rbw//", rendered)
        self.assertIn("\033[33m", rendered)

    def test_gfm_task_markers_and_strikethrough(self):
        rendered = render_terminal("- [x] shipped\n- [ ] next\n~~outdated~~")
        self.assertIn("[x]", rendered)
        self.assertIn("[ ]", rendered)
        self.assertIn("\033[9moutdated", rendered)

    def test_gfm_table_renders_as_aligned_terminal_grid(self):
        source = "| Feature | Status |\n| :--- | ---: |\n| Tables | ready |\n| ~~Old approach~~ | replaced |"
        rendered = render_terminal(source)
        self.assertRegex(rendered, r"\+-{14}\+-{10}\+")
        self.assertIn("| Feature", rendered)
        self.assertIn("| Status", rendered)
        self.assertNotIn("| :--- | ---: |", rendered)
        self.assertIn("\033[9mOld approach\033[0m", rendered)

    def test_flip_uses_terminal_friendly_digit_mappings(self):
        rendered = render_terminal("/!!!/Hello MDXL 42 7/!!!/")
        for unsupported in ("\\u1105", "\\u3134", "\\u02e5", "\\u3105"):
            self.assertNotIn(unsupported, rendered)
        self.assertIn("ollǝH", rendered)

    def test_gfm_alerts_render_as_labeled_callouts(self):
        source = "> [!TIP]\n> Use callouts for a tip.\n> Keep the second line."
        rendered = render_terminal(source)
        self.assertIn("TIP:", rendered)
        self.assertIn("Use callouts for a tip.", rendered)
        self.assertIn("    Keep the second line.", rendered)
        self.assertNotIn("[!TIP]", rendered)
        self.assertNotIn("> Use callouts", rendered)

    def test_arrows_and_shortcode(self):
        rendered = render_terminal("[[==>>]] [[<<==]] [[<=>>]] :check:")
        for symbol in ("➜", "⬅", "⇄", "✅"):
            self.assertIn(symbol, rendered)


if __name__ == "__main__":
    unittest.main()
