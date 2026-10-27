import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { Button } from "@heroui/react";
import "./styles.css";

const samples = [
  {name:"True color",source:"/col//signal green /col#B7F77A//",description:"Use a six-digit hex value to give inline text its own color.",preview:<span className="lime">signal green</span>},
  {name:"Rainbow",source:"/rbw//spectrum//rbw//",description:"Cycle through a vivid palette, one character at a time.",preview:<span className="rainbow"><i>s</i><i>p</i><i>e</i><i>c</i><i>t</i><i>r</i><i>u</i><i>m</i></span>},
  {name:"Highlight",source:"//hl//pay attention//hl//",description:"Mark a phrase without writing HTML.",preview:<mark>pay attention</mark>},
  {name:"Redaction style",source:"/red//old approach/red//",description:"Show superseded text with a strike-through treatment.",preview:<del>old approach</del>},
  {name:"Keyboard key",source:"//key//Ctrl+C//key//",description:"Give shortcuts a tidy keycap appearance.",preview:<kbd>Ctrl+C</kbd>},
  {name:"Progress bar",source:"/bar//72//",description:"Render a clear progress indicator, clamped to 0–100.",preview:<span className="progress"><i><b/></i><small>72%</small></span>},
  {name:"Invisible ink",source:"||||[hidden in plain sight]||||",description:"Hover or keyboard-focus the words in a browser preview to reveal them.",preview:<span className="invisible">hidden in plain sight</span>},
  {name:"Upside down",source:"/!!!/turn it around/!!!/",description:"Flip supported glyphs into an upside-down Unicode approximation.",preview:<span className="flip">uʍop ǝpᴉsdn</span>},
  {name:"Headings",source:"-# Micro one\n-## Micro two\n-### Micro three\n#### Subheading",description:"The three micro-header levels coexist with standard Markdown #### headings.",preview:<span className="heading-sample"><small>MICRO ONE</small><i>Micro two</i><em>Micro three</em><strong>Subheading</strong></span>},
  {name:"Directional arrows",source:"[[==>>]] [[<<==]] [[<=>>]]",description:"Tap the arrows in a rendered document to cycle the direction.",preview:<span className="arrows">➜　⬅　⇄</span>}
];

const featureCards = [
  ["01","Text with intent","Color, highlight, redact, or conceal a phrase without embedding HTML in your source."],
  ["02","Structure that scales","Keep standard Markdown and recover the full heading family, including ####."],
  ["03","One file, two renderers","Use terminal ANSI colors for quick reads and a live browser preview for longer documents."],
  ["04","A place in your editor","Kate's KSyntaxHighlighting definition brings token colors and completions into the writing flow."]
];


const BASE = "/mdxl/";
const ICON = BASE + "mdxl-mark.svg";
const docPages = [
 {id:"guide",label:"Guide",kicker:"START HERE",title:"A little extra meaning.",intro:"MDXL keeps Markdown familiar and gives it a small expressive layer for the information you want people to notice.",sections:[
  {eyebrow:"THE MENTAL MODEL",title:"Write the source first.",body:"An MDXL file is still a text file. Its delimiters are visible, diff cleanly in version control, and remain understandable even when a renderer is not installed. Use regular Markdown wherever it already does the job."},
  {eyebrow:"YOUR FIRST RENDER",title:"Three steps from source to preview.",body:"Install the tools, open the sample, and choose the renderer you need. The terminal renderer is fast for text-first workflows; the browser preview adds richer styling and refreshes after saves.",code:"chmod +x install.sh\n./install.sh\nmdxl-cli demo.mdxl\nmdxl-preview demo.mdxl"},
  {eyebrow:"GOOD PRACTICE",title:"Add emphasis, not noise.",body:"Pick one or two styles for a document and use them consistently. Use color for status, highlights for important takeaways, and progress bars for a measurable quantity. Keep the underlying words meaningful without decoration."}]},
 {id:"syntax",label:"Syntax",kicker:"REFERENCE / 01",title:"The extra layer, token by token.",intro:"A practical reference to MDXL's custom syntax, including the three micro-header levels and the independent Markdown level-four heading.",sections:[
  {eyebrow:"HEADINGS",title:"The complete heading family.",body:"Dash-prefixed headings are deliberately compact variants. The four-hash heading remains standard Markdown level four and must not be consumed as a micro-heading.",table:[["Source","Use"],["-# Heading","Micro-header · level 1"],["-## Heading","Micro-header · level 2"],["-### Heading","Micro-header · level 3"],["#### Heading","Markdown heading · level 4"]]},
  {eyebrow:"INLINE TEXT",title:"Style a phrase.",body:"Pair the opening delimiter with its matching closing delimiter. The color token includes a six-digit hex color; other effects use short, memorable markers.",table:[["Source token","Effect"],["/col//Signal /col#B7F77A//","Hex true color"],["/rbw//Spectrum//rbw//","Rainbow, character by character"],["//hl//Important//hl//","Highlight"],["/red//Old wording/red//","Strikethrough styling"],["//key//Ctrl+C//key//","Keyboard keycap"],["||||[Hidden note]||||","Invisible ink in the preview"],["/!!!/Turn around/!!!/","Upside-down Unicode approximation"]]},
  {eyebrow:"INLINE CUES",title:"Add a quick signal.",body:"Progress values are limited to 0–100. Arrow tokens display direction glyphs and can cycle in the browser renderer. Supported shortcode examples include :check:, :rocket:, :warn:, :fire:, and :star:; unsupported names are kept as written.",table:[["Token","Meaning"],["/bar//72//","Progress at 72%"],["[[==>>]]","Right arrow"],["[[<<==]]","Left arrow"],["[[<=>>]]","Bidirectional arrow"]]},
  {eyebrow:"CODE PRESENTATION",title:"Code that waits for its reader.",body:"A five-backtick block creates a dedicated code panel in the preview. The language label is a presentation hint, not an execution request. Nothing inside a document runs automatically."}]},
 {id:"installation",label:"Install",kicker:"SETUP / 02",title:"From clone to command line.",intro:"Install MDXL without administrator access. The installer keeps the preview dependency in its own virtual environment instead of modifying system Python.",sections:[
  {eyebrow:"REQUIREMENTS",title:"A small local toolchain.",body:"Use Python 3.9 or newer and a Linux shell for the provided installer. Kate is optional; it is only needed for the editor syntax integration. The preview renderer uses Python Markdown."},
  {eyebrow:"INSTALL",title:"Run the bundled installer.",body:"Run these commands from the repository root, where install.sh, mdxl_cli.py, mdxl_preview.py, and mdxl.xml live.",code:"chmod +x install.sh\n./install.sh"},
  {eyebrow:"MANUAL PREVIEW DEPENDENCY",title:"Keep it out of system Python.",body:"The installer creates a dedicated virtual environment under ~/.local/share/mdxl/venv. For a manual development environment, install from the repository's requirements file.",code:"python3 -m venv .venv\n. .venv/bin/activate\npython -m pip install -r requirements-preview.txt"},
  {eyebrow:"TROUBLESHOOTING",title:"When commands are not found.",body:"Check that ~/.local/bin is on PATH, then open a new terminal or source your shell profile. If Kate does not highlight .mdxl files, confirm mdxl.xml is in the per-user KSyntaxHighlighting directory and restart Kate. If the preview port is busy, choose another starting port."}]},
 {id:"renderers",label:"Renderers",kicker:"TOOLS / 03",title:"One source, different surfaces.",intro:"Choose a renderer based on what you need: read in a terminal, review a live preview, export HTML, or edit with token-aware highlighting.",sections:[
  {eyebrow:"TERMINAL",title:"mdxl-cli",body:"The terminal renderer maps supported tokens to ANSI colors and Unicode. It has no HTML dependency and never executes code, so it works well for a quick review or terminal-first workflow.",code:"mdxl-cli demo.mdxl"},
  {eyebrow:"LOCAL BROWSER",title:"mdxl-preview",body:"The browser renderer serves the document on 127.0.0.1, opens the local preview by default, and refreshes after the file changes. If the starting port is busy, it tries up to nine subsequent ports.",code:"mdxl-preview demo.mdxl\nmdxl-preview demo.mdxl --no-open --port 8420"},
  {eyebrow:"OUTPUT MODES",title:"Preview, export, or pipe.",body:"The --stdout option prints rendered HTML to standard output. --export writes HTML to a file and accepts an optional output path. The --live flag enables save-and-refresh polling.",code:"mdxl-preview demo.mdxl --stdout\nmdxl-preview demo.mdxl --export\nmdxl-preview demo.mdxl --export ./demo.html"},
  {eyebrow:"EDITOR",title:"Kate syntax and completions.",body:"The mdxl.xml definition registers .mdxl, highlights custom tokens and headings, and provides completion suggestions. It is installed in the user's syntax-highlighting directory; restart Kate after installation."}]},
 {id:"examples",label:"Examples",kicker:"PATTERNS / 04",title:"Ready-made patterns to borrow.",intro:"MDXL is most useful when each effect carries meaning. Start with these small patterns, then adapt their source to your own documents.",sections:[
  {eyebrow:"PROJECT STATUS",title:"A compact status note.",body:"Use a color for build state, a highlight for the next action, and a progress bar for a measurable checkpoint.",code:"-# RELEASE STATUS\nBuild: /col//passing /col#B7F77A//\nNext action: //hl//verify docs deployment//hl//\nProgress: /bar//72//"},
  {eyebrow:"CHANGELOG",title:"Make a release readable at a glance.",body:"Keep the standard Markdown hierarchy, then use compact headings to group small details. The four-hash heading remains a normal Markdown heading.",code:"## 1.4.0\n\n-# Added\n- Interactive syntax reference\n- Copyable preview code\n\n-## Fixed\n- Restored #### heading support\n- Better preview install isolation\n\n#### Notes\n- Existing Markdown stays readable."},
  {eyebrow:"DOCUMENTATION",title:"Call out the important line.",body:"Put a clear highlight next to useful context instead of decorating every paragraph.",code:"#### Before you begin\nInstall the CLI first, then //hl//run the preview against a real file//hl//.\n\nShortcut: //key//Ctrl+C//key//"},
  {eyebrow:"REVIEW A NOTE",title:"Hide spoilers, not meaning.",body:"Invisible ink works best for a spoiler, answer, or optional note. It reveals on hover or keyboard focus in the browser preview; in a terminal it uses dark ANSI foreground and background.",code:"Answer: ||||[42]||||\n\nGo to the next step [[==>>]]"}]},
 {id:"about",label:"About",kicker:"PROJECT / 05",title:"Plain-text first, by design.",intro:"MDXL is a small Markdown extension project. Its aim is to add visual emphasis without making the document depend on a complex editor or a web runtime.",sections:[
  {eyebrow:"PRINCIPLE 01",title:"Readable source comes first.",body:"The tokens are short and visible, so a document remains a text file that can be reviewed, diffed, and maintained in Git. Markdown is the baseline rather than something to replace."},
  {eyebrow:"PRINCIPLE 02",title:"Renderers should be predictable.",body:"The terminal renderer maps syntax to text and ANSI sequences. The browser renderer decorates content, escapes raw HTML tags, and displays five-backtick code blocks as copyable code. The preview never executes document code automatically."},
  {eyebrow:"PRINCIPLE 03",title:"Keep the tools local.",body:"Preview serves on loopback rather than exposing the document to the local network. Static HTML export gives a portable artifact when a live server is not needed."},
  {eyebrow:"CONTRIBUTING",title:"Small fixes, validated behavior.",body:"When making changes, update the renderer tests and syntax guide together. Run the Python unit tests, validate mdxl.xml, and build the Vite site before opening a pull request.",code:"python -m unittest discover -s tests -v\npython -m py_compile mdxl_cli.py mdxl_preview.py\ncd website && npm run build"}]}
];
function BrandMark(){return <img className="brand-svg" src={ICON} alt="" width="34" height="34"/>;}
function SiteNav({current="home"}){
 return <header className="nav"><a className="logo" href={BASE} aria-label="MDXL home"><BrandMark/><span>MDXL</span></a><nav aria-label="Main navigation">{docPages.map(p=><a key={p.id} className={current===p.id?"nav-current":""} href={BASE+p.id+"/"}>{p.label}</a>)}<a className="github" href="https://github.com/trail-b1az3r/mdxl" target="_blank" rel="noreferrer">GitHub <span>↗</span></a></nav></header>;
}
function SiteFooter(){return <footer className="footer wrap"><a className="logo" href={BASE}><BrandMark/><span>MDXL</span></a><p>Plain text, with a little more intention.</p><div><a href="https://github.com/trail-b1az3r/mdxl">GitHub ↗</a><a href={BASE+"syntax/"}>Syntax reference ↗</a><a href="https://github.com/trail-b1az3r/mdxl/blob/main/LICENSE">MIT license ↗</a></div><small>MDXL · OPEN SOURCE</small></footer>;}
function CopyCode({text,label="Copy example"}){
 const [copied,setCopied]=useState(false);
 async function run(){try{await navigator.clipboard.writeText(text);setCopied(true);window.setTimeout(()=>setCopied(false),1400);}catch{setCopied(false);}}
 return <button className="copy-button" onClick={run}>{copied?"Copied":label} <span>↗</span></button>;
}
function DocumentationPage({page}){
 const [tocOpen,setTocOpen]=useState(false);
 return <div className="app-shell docs-shell"><SiteNav current={page.id}/><main>
  <section className="doc-hero wrap"><div className="doc-kicker"><span className="doc-kicker-mark"><BrandMark/></span><span>{page.kicker} <i/> MDXL DOCUMENTATION</span></div><h1>{page.title}</h1><p>{page.intro}</p><div className="doc-hero-meta"><span className="tonal-chip">Plain-text first</span><span className="tonal-chip lavender">Open source</span><span className="tonal-chip blue">Local renderers</span></div></section>
  <div className="doc-layout wrap"><aside className="doc-sidebar"><div className="sidebar-heading">EXPLORE MDXL</div>{docPages.map((p,i)=><a key={p.id} className={p.id===page.id?"side-link side-active":"side-link"} href={BASE+p.id+"/"}><span>{String(i+1).padStart(2,"0")}</span>{p.label}<b>{p.id===page.id?"●":"↗"}</b></a>)}<div className="sidebar-card"><span className="sidebar-orb">M<span>D</span></span><b>Learn by example</b><p>Open the interactive syntax explorer to inspect and copy a token.</p><a href={BASE+"#explore"}>Explore syntax ↗</a></div></aside>
   <article className="doc-content"><div className="doc-content-top"><span>MDXL / {page.id.toUpperCase()}</span><button className="toc-toggle" onClick={()=>setTocOpen(v=>!v)}>{tocOpen?"Hide contents":"On this page"} <span>{tocOpen?"−":"+"}</span></button></div>{tocOpen&&<div className="toc-panel">{page.sections.map((s,i)=><a key={s.title} href={"#section-"+i}>{s.title}</a>)}</div>}
   {page.sections.map((s,i)=><section className="doc-section" id={"section-"+i} key={s.title}><div className="doc-eyebrow"><span>{String(i+1).padStart(2,"0")}</span>{s.eyebrow}</div><h2>{s.title}</h2><p>{s.body}</p>{s.code&&<div className="doc-code"><div><span>SOURCE</span><CopyCode text={s.code}/></div><pre><code>{s.code}</code></pre></div>}{s.table&&<div className="doc-table-wrap"><table><thead><tr>{s.table[0].map(v=><th key={v}>{v}</th>)}</tr></thead><tbody>{s.table.slice(1).map((row,j)=><tr key={j}>{row.map((v,k)=><td key={k}>{k===0?<code>{v}</code>:v}</td>)}</tr>)}</tbody></table></div>}</section>)}
   <div className="doc-next"><div><span className="kicker">KEEP EXPLORING</span><h3>{page.id==="syntax"?"Try the patterns in context.":"Open the syntax reference."}</h3><p>Move from the guide to the interactive specimen and see how MDXL tokens read when rendered.</p></div><a href={BASE+(page.id==="syntax"?"examples/":"syntax/")}>Continue ↗</a></div>
  </article></div></main><SiteFooter/></div>;
}
function SiteRouter(){
 const path=window.location.pathname.replace(/^\/mdxl\/?/,"").replace(/\/+$/,"");
 const slug=path.split("/")[0]||"home";
 const page=docPages.find(p=>p.id===slug);
 return page?<DocumentationPage page={page}/>:<HomePage/>;
}

function HomePage() {
  const [selected,setSelected] = useState(0);
  const [notice,setNotice] = useState("");
  async function copy(text) {
    try {
      await navigator.clipboard.writeText(text);
      setNotice("Copied to clipboard");
      window.setTimeout(()=>setNotice(""),1400);
    } catch {
      setNotice("Clipboard unavailable");
      window.setTimeout(()=>setNotice(""),1800);
    }
  }
  const item=samples[selected];
  return <div className="app-shell">
    <SiteNav/>
    <main>
      <section className="hero wrap" id="home">
        <div className="hero-copy">
          <div className="eyebrow"><span/> MARKDOWN, WITH ANOTHER DIMENSION</div>
          <h1>Plain text.<br/><em>Extra dimension.</em></h1>
          <p>MDXL adds a small, expressive second layer to Markdown: color, hidden notes, compact headings, progress bars, and more. Still readable in the source. Better when rendered.</p>
          <div className="actions"><Button className="cta" onPress={()=>document.querySelector("#install")?.scrollIntoView({behavior:"smooth"})}>Get started <span>↗</span></Button><a href="#explore" className="explore-link">Explore the syntax <span>↓</span></a></div>
          <div className="micro-meta"><span>OPEN SOURCE</span><b/> <span>PLAIN-TEXT FIRST</span><b/> <span>LOCAL RENDERERS</span></div>
        </div>
        <div className="editor-card">
          <div className="window-top"><div className="window-dots"><i/><i/><i/></div><span>demo.mdxl</span><small>MDXL / 01</small></div>
          <div className="code-lines">
            <div><span>01</span><label>-#</label><strong>A little more meaning</strong></div>
            <div><span>02</span><label>-##</label><strong>without more markup.</strong></div>
            <div className="blank"><span>03</span></div>
            <div><span>04</span><label className="pink">/col//</label><em>readable</em><label className="pink"> /col#B7F77A//</label></div>
            <div><span>05</span><label className="purple">//hl//</label><strong className="highlight-code">important</strong><label className="purple">//hl//</label></div>
            <div><span>06</span><label>/bar//</label><em>72</em><label>//</label><i className="tiny-progress"><b/></i></div>
            <div><span>07</span><label>||||[</label><small>hidden in plain sight</small><label>]||||</label></div>
            <div className="blank"><span>08</span></div>
            <div><span>09</span><label>####</label><a>One file. More places.</a></div>
          </div>
          <div className="rendered-bar"><div><i/> RENDERED PREVIEW</div><p>Small syntax. <em>Clear signal.</em><b>MDXL</b></p><span>➜　⬅　⇄</span></div>
          <div className="float-label float-one">No HTML required</div><div className="float-label float-two">Source stays human</div>
        </div>
        <div className="hero-index"><strong>01 / 04</strong><i/><span>SCROLL TO DISCOVER</span></div>
      </section>

      <section className="intro"><div className="wrap intro-inner"><span className="kicker">THE IDEA</span><p>Markdown gives you the structure. <strong>MDXL adds the signal.</strong> Small, explicit tokens make documents more expressive without making the source harder to maintain.</p><span className="monogram">M<span>D</span></span></div></section>

      <section className="section wrap" id="why">
        <div className="section-title"><div><span className="kicker">BUILT FOR REAL DOCUMENTS</span><h2>Small syntax.<br/><em>Useful range.</em></h2></div><p>Not a replacement for Markdown. A focused extension for the moments where plain formatting feels a little too plain.</p></div>
        <div className="feature-grid">{featureCards.map(([n,title,text])=><article className="feature" key={n}><div><span>{n}</span><em>↗</em></div><h3>{title}</h3><p>{text}</p></article>)}</div>
        <div className="section-foot"><i/> THE SAME SOURCE, DIFFERENT SURFACES.</div>
      </section>

      <section className="showcase" id="explore"><div className="wrap">
        <div className="section-title"><div><span className="kicker">SYNTAX EXPLORER</span><h2>Meet the<br/><em>extra layer.</em></h2></div><p>Choose a syntax token to inspect its source and preview the intended effect. The source stays legible before it is rendered.</p></div>
        <div className="workbench">
          <aside className="sample-list" aria-label="Syntax examples">{samples.map((sample,i)=><button className={i===selected?"sample active":"sample"} key={sample.name} onClick={()=>setSelected(i)}><span>{String(i+1).padStart(2,"0")}</span>{sample.name}<b>↗</b></button>)}</aside>
          <div className="sample-detail"><div className="sample-head"><span>LIVE SPECIMEN</span><i/></div><div className="result"><label>RENDERED RESULT</label><div className="result-stage">{item.preview}</div><p>{item.description}</p></div><div className="source-sample"><div><span>SOURCE TOKEN</span><button onClick={()=>copy(item.source)}>Copy token ↗</button></div><pre>{item.source}</pre></div></div>
        </div>
        <div className="showcase-foot"><span>10 EXAMPLES</span><span>SELECT A PATTERN TO CHANGE THE SPECIMEN</span><a href="https://github.com/trail-b1az3r/mdxl/blob/main/docs/syntax.md">Full syntax guide ↗</a></div>
      </div></section>

      <section className="section wrap" id="install">
        <div className="section-title"><div><span className="kicker">FROM SOURCE TO SIGNAL</span><h2>Three steps.<br/><em>One document.</em></h2></div><p>Keep a .mdxl file in your project and pick the renderer that fits the moment.</p></div>
        <div className="steps">
          <article><span>01</span><div className="step-icon">.mdxl</div><h3>Write</h3><p>Use familiar Markdown and add tokens where extra visual emphasis is useful.</p><code>demo.mdxl</code></article>
          <article><span>02</span><div className="step-icon terminal">›_</div><h3>Render</h3><p>Use the terminal for a quick read or a live browser preview for longer docs.</p><code>mdxl-cli demo.mdxl</code></article>
          <article><span>03</span><div className="step-icon editor">▤</div><h3>Keep editing</h3><p>Open the same file in Kate with syntax colors and completion suggestions.</p><code>edit · save · preview</code></article>
        </div>
        <div className="install-box"><div><span className="kicker">QUICK INSTALL</span><h3>Start with the essentials.</h3><p>The installer sets up both renderers, Kate syntax, and a private environment for preview dependencies.</p><a href="https://github.com/trail-b1az3r/mdxl/blob/main/docs/installation.md">Installation notes ↗</a></div><div className="terminal-window"><header><span>TERMINAL</span><button onClick={()=>copy("chmod +x install.sh\n./install.sh")}>Copy commands</button></header><pre><span>$</span> chmod +x install.sh{"\n"}<span>$</span> ./install.sh{"\n"}<small># Restart Kate and open a new terminal.</small></pre></div></div>
      </section>

      <section className="safety-note"><div className="wrap safety-inner"><div><span className="kicker">A NOTE ON CODE BLOCKS</span><h2>Show the code.<br/><em>Don't surprise the reader.</em></h2></div><p>Five-backtick MDXL blocks are presented as copyable code in the browser preview. They do not run automatically. Execution belongs to an explicit user action outside the renderer.</p></div></section>
    <section className="section wrap more-reading"><div className="section-title"><div><span className="kicker">GO A LITTLE DEEPER</span><h2>There's more<br/><em>in the docs.</em></h2></div><p>A growing guide to the syntax, tools, examples, and practical ways to use MDXL.</p></div><div className="reading-grid">{docPages.map((p,i)=><a className={"reading-card reading-"+i} key={p.id} href={BASE+p.id+"/"}><span>{String(i+1).padStart(2,"0")} / {p.kicker}</span><h3>{p.label}</h3><p>{p.intro}</p><b>Explore page ↗</b></a>)}</div></section>
  <section className="section wrap more-reading"><div className="section-title"><div><span className="kicker">GO A LITTLE DEEPER</span><h2>There's more<br/><em>in the docs.</em></h2></div><p>A growing guide to the syntax, tools, examples, and practical ways to use MDXL.</p></div><div className="reading-grid">{docPages.map((p,i)=><a className={"reading-card reading-"+i} key={p.id} href={BASE+p.id+"/"}><span>{String(i+1).padStart(2,"0")} / {p.kicker}</span><h3>{p.label}</h3><p>{p.intro}</p><b>Explore page ↗</b></a>)}</div></section>
  </main>
    <SiteFooter/>
    {notice && <div className="toast" role="status">{notice}</div>}
  </div>;
}

createRoot(document.getElementById("root")).render(<SiteRouter />);
