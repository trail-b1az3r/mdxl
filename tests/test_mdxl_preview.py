import html
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
        self.assertIn('<h4 id="four">four', rendered)

    def test_fenced_source_is_not_transformed_or_executed(self):
        source = "```text\n/rbw//literal//rbw//\n```"
        rendered = render_mdxl(source)
        self.assertIn("/rbw//literal//rbw//", rendered)
        self.assertNotIn('class="mdxl-rainbow"', rendered)
        self.assertNotIn("runCode", rendered)

    def test_gfm_tables_tasks_strikethrough_and_autolinks(self):
        source = """| Feature | Support |
| :--- | ---: |
| Tables | yes |

- [x] shipped
- [ ] next

~~outdated~~ and https://example.com and user@example.com"""
        rendered = render_mdxl(source)
        self.assertIn("<table>", rendered)
        self.assertIn('type="checkbox"', rendered)
        self.assertIn("checked", rendered)
        self.assertIn("<del>outdated</del>", rendered)
        self.assertIn('href="https://example.com"', rendered)
        self.assertIn('href="mailto:user@example.com"', html.unescape(rendered))

    def test_markdown_extra_footnotes_definitions_abbreviations_and_heading_ids(self):
        source = """## Named heading {#named-heading}

MDXL supports HTML[^note].

*[HTML]: Hyper Text Markup Language

MDXL
: A Markdown extension.

[^note]: A footnote definition."""
        rendered = render_mdxl(source)
        self.assertIn('id="named-heading"', rendered)
        self.assertIn('<abbr title="Hyper Text Markup Language">HTML</abbr>', rendered)
        self.assertIn("<dl>", rendered)
        self.assertIn("A Markdown extension.", rendered)
        self.assertIn("footnote", rendered.lower())

    def test_github_alerts_render_as_tonal_admonitions(self):
        rendered = render_mdxl("> [!WARNING]\n> Stop and check this first.")
        self.assertIn('class="admonition warning"', rendered)
        self.assertIn("Warning", rendered)
        self.assertIn("Stop and check this first.", rendered)

    def test_five_backtick_code_is_copyable_and_tokens_stay_literal(self):
        source = "`````text\n/rbw//literal//rbw//\n`````"
        rendered = render_mdxl(source)
        self.assertIn('class="exec-block"', rendered)
        self.assertIn("/rbw//literal//rbw//", rendered)
        self.assertNotIn('class="mdxl-rainbow"', rendered)

    def test_unsafe_heading_attributes_and_link_schemes_are_removed(self):
        rendered = render_mdxl('## Heading {onclick="alert(1)"}\n\n[unsafe](javascript:alert(1))')
        self.assertNotIn("onclick=", rendered.lower())
        self.assertNotIn('href="javascript:', rendered.lower())

    def test_raw_html_is_escaped(self):
        rendered = render_mdxl("<script>alert(1)</script>")
        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<script>alert(1)</script>", rendered)


if __name__ == "__main__":
    unittest.main()
