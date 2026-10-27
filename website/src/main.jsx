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

function App() {
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
    <header className="nav">
      <a className="logo" href="#home"><span className="logo-icon">M<span>D</span></span> MDXL</a>
      <nav aria-label="Main navigation"><a href="#why">Why MDXL</a><a href="#explore">Syntax</a><a href="#install">Get started</a><a className="github" href="https://github.com/trail-b1az3r/mdxl" target="_blank" rel="noreferrer">GitHub <span>↗</span></a></nav>
    </header>
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
    </main>
    <footer className="footer wrap"><a className="logo" href="#home"><span className="logo-icon">M<span>D</span></span> MDXL</a><p>Plain text, with a little more intention.</p><div><a href="https://github.com/trail-b1az3r/mdxl">GitHub ↗</a><a href="https://github.com/trail-b1az3r/mdxl/blob/main/docs/syntax.md">Syntax reference ↗</a><a href="https://github.com/trail-b1az3r/mdxl/blob/main/LICENSE">MIT license ↗</a></div><small>MDXL · OPEN SOURCE</small>
    </footer>
    {notice && <div className="toast" role="status">{notice}</div>}
  </div>;
}

createRoot(document.getElementById("root")).render(<App />);
