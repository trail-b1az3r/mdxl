import html
import unittest

from mdxl_preview import _translate_with_provider, render_mdxl


def _body(source):
    """The rendered document without the page's own styles and scripts."""
    return render_mdxl(source).split("<article>", 1)[1].rsplit("</article>", 1)[0]


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

    def test_plus_headings_nested_quotes_and_striped_through(self):
        source = """+# Compact detail
++# Fine detail

> Main quote
>> Nested quote

This is ~~~~striped-through text~~~~."""
        rendered = render_mdxl(source)
        self.assertIn('class="mdxl-micro-plus-1"', rendered)
        self.assertIn('class="mdxl-micro-plus-2"', rendered)
        self.assertGreaterEqual(rendered.count("<blockquote>"), 2)
        self.assertIn('class="mdxl-striped-through"', rendered)
        self.assertIn("striped-through text", rendered)
        self.assertIn("repeating-linear-gradient(135deg", rendered)

    def test_fenced_source_is_not_transformed_or_executed(self):
        source = "```text\n/rbw//literal//rbw//\n```"
        rendered = render_mdxl(source)
        self.assertIn("/rbw//literal//rbw//", rendered)
        self.assertNotIn('class="mdxl-rainbow"', rendered)
        self.assertNotIn("runCode", rendered)

    def test_executable_javascript_fence_requires_a_run_button(self):
        source = chr(96) * 3 + "js\nconsole.log('hello from MDXL');\n" + chr(96) * 3
        rendered = render_mdxl(source)
        self.assertIn('class="exec-block"', rendered)
        self.assertIn('class="run-code">Run JavaScript</button>', rendered)
        self.assertIn('class="copy-code">Copy code</button>', rendered)
        self.assertIn("sandbox", rendered)
        self.assertIn("Execution stopped after 10 seconds.", rendered)

    def test_generated_page_has_valid_script_newline_escape_and_nonrepeating_background(self):
        rendered = render_mdxl("A simple paragraph.")
        # Python must emit a literal \\n escape inside the JavaScript source,
        # rather than inserting an actual newline into a single-quoted JS string.
        self.assertIn(r"safeCode + '\n' + scriptClose", rendered)
        self.assertNotIn("safeCode + '\n' + scriptClose", rendered)
        self.assertIn("background-repeat:no-repeat", rendered)

    def test_auto_translation_directive_and_joke_styles(self):
        translated = render_mdxl("//autoT//Hola, mundo.//en")
        self.assertIn('class="mdxl-translation"', translated)
        self.assertIn('data-target="en"', translated)
        self.assertIn("Hola, mundo.", translated)
        self.assertIn("fetch('/__translate'", translated)
        self.assertIn(r"/\bcomputadora\b/gi", translated)
        self.assertNotIn(chr(8), translated)

        pirate = render_mdxl("//autoT//Hello friend//joke1")
        self.assertIn('class="mdxl-joke-translation"', pirate)
        self.assertIn("Pirate English", pirate)
        self.assertIn("Arrr! Ahoy matey", pirate)

    def test_translation_rejects_invalid_target_codes(self):
        with self.assertRaises(ValueError):
            _translate_with_provider("Hello", ["en"])
        with self.assertRaises(ValueError):
            _translate_with_provider("Hello", "not-a-language")

    def test_formatted_document_blocks_apa_mla_and_optional_headers(self):
        apa = render_mdxl(">>>[APA](Research Title)(Author Name)(Course)(Date)\nThis is the **formatted body**.")
        self.assertIn('class="mdxl-format mdxl-format-apa"', apa)
        self.assertIn("Research Title", apa)
        self.assertIn("Author Name", apa)
        self.assertIn("This is the <strong>formatted body</strong>.", apa)

        mla = render_mdxl(">>>[MLA](Student Name)(Instructor)\nA short paper.")
        self.assertIn('class="mdxl-format mdxl-format-mla"', mla)
        self.assertIn("Student Name", mla)
        self.assertIn("A short paper.", mla)

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


    def test_extended_inline_tokens(self):
        rendered = _body(
            "/u//under/u// /big//big/big// /sml//small/sml// /bdg//Beta/bdg// /bdg#2E8BF2//v2/bdg// "
            "/grad#FF0000#0000FF//ab/grad// /wave//hi/wave// /glow//neon/glow// /tip//Word//Explained/tip//"
        )
        for token in ('class="mdxl-underline"', 'class="mdxl-big"', 'class="mdxl-small"', 'class="mdxl-badge"',
                      'class="mdxl-gradient"', 'class="mdxl-wave"', 'class="mdxl-glow"', 'class="mdxl-tip"'):
            self.assertIn(token, rendered)
        self.assertIn("background-color:#2E8BF2", rendered)
        self.assertIn("color:#ff0000", rendered)   # the gradient starts on the first colour
        self.assertIn("color:#0000ff", rendered)   # and ends on the second
        self.assertIn('title="Explained"', rendered)
        self.assertNotIn("/u//", rendered)

    def test_ruby_survives_the_sanitizer(self):
        rendered = _body("/rb//漢字//かんじ/rb//")
        self.assertIn("<ruby>漢字", rendered)
        self.assertIn("<rt>かんじ</rt>", rendered)

    def test_centred_line(self):
        rendered = _body("->A **centred** line<-")
        self.assertIn('class="mdxl-center"', rendered)
        self.assertIn("<strong>centred</strong>", rendered)
        self.assertNotIn("<br", rendered.split('class="mdxl-center"', 1)[1].split("</p>", 1)[0])

    def test_columns_hold_a_nested_card(self):
        rendered = _body("::: columns\n### Before\nOld\n:::|\n::: card Side\n**New**\n:::\n:::")
        self.assertIn('class="mdxl-columns"', rendered)
        self.assertEqual(rendered.count('class="mdxl-column"'), 2)
        self.assertIn('class="mdxl-card"', rendered)
        self.assertIn("Side", rendered)
        self.assertIn("<strong>New</strong>", rendered)
        self.assertNotIn(":::", rendered)

    def test_timeline_and_chat(self):
        rendered = _body("::: timeline\n2024 :: The **first**\n2025 :: Next\n:::\n\n"
                               "::: chat\nAna: Hi\nBen: Hello *there*\nAna: Bye\n:::")
        self.assertIn('class="mdxl-timeline"', rendered)
        self.assertIn('class="mdxl-when">2024', rendered)
        self.assertIn("<strong>first</strong>", rendered)
        self.assertEqual(rendered.count("mdxl-msg-left"), 2)
        self.assertEqual(rendered.count("mdxl-msg-right"), 1)
        self.assertIn("<em>there</em>", rendered)

    def test_new_syntax_stays_literal_in_code(self):
        rendered = _body("```\n/u//x/u//\n::: card T\nbody\n:::\n```")
        self.assertIn("/u//x/u//", rendered)
        self.assertIn("::: card T", rendered)
        self.assertNotIn('class="mdxl-card"', rendered)

    def test_block_text_is_escaped(self):
        rendered = _body("::: chat\n<script>x</script>: <img src=x onerror=alert(1)>\n:::")
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("<img", rendered)
        self.assertIn('class="mdxl-who">&lt;script&gt;x&lt;/script&gt;</span>', rendered)   # escaped once

if __name__ == "__main__":
    unittest.main()
