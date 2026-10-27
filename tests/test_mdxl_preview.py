import unittest

from mdxl_preview import render_mdxl


class BrowserRendererTests(unittest.TestCase):
    def test_restored_text_effects_render(self):
        rendered = render_mdxl("/col//lime /col#B7F77A// /rbw//rainbow//rbw// //hl//important//hl// /red//old/red// //key//Ctrl+C//key// /bar//70//")
        for token in ('class="mdxl-color"', 'class="mdxl-rainbow"', 'class="mdxl-highlight"', 'class="mdxl-redact"', 'class="mdxl-key"'):
            self.assertIn(token, rendered)
        self.assertIn('aria-valuenow="70"', rendered)

    def test_microheaders_and_h4(self):
        rendered = render_mdxl("-# one\n\n-## two\n\n-### three\n\n#### four")
        self.assertIn('class="mdxl-micro-1"', rendered)
        self.assertIn('class="mdxl-micro-2"', rendered)
        self.assertIn('class="mdxl-micro-3"', rendered)
        self.assertIn("<h4>four</h4>", rendered)

    def test_fenced_source_is_not_transformed_or_executed(self):
        source = "```text\n/rbw//literal//rbw//\n```"
        rendered = render_mdxl(source)
        self.assertIn("/rbw//literal//rbw//", rendered)
        self.assertNotIn('class="mdxl-rainbow"', rendered)
        self.assertNotIn("runCode", rendered)

    def test_raw_html_is_escaped(self):
        rendered = render_mdxl("<script>alert(1)</script>")
        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<script>alert(1)</script>", rendered)


if __name__ == "__main__":
    unittest.main()
