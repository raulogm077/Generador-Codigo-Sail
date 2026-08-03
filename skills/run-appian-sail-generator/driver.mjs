#!/usr/bin/env node
/**
 * Driver for the run-appian-sail-generator skill.
 *
 * Validates a .sail file produced by the appian-sail-generator skill
 * and renders a self-contained HTML preview (dark-theme, syntax-
 * highlighted, with an inventory panel). Opens the preview in the
 * default browser unless --no-open is passed.
 *
 * Usage:
 *   node driver.mjs                       # picks newest .sail under <unit>/output/
 *   node driver.mjs path/to/file.sail
 *   node driver.mjs file.sail --no-open
 *   node driver.mjs file.sail --out file.html
 *
 * Exit codes:
 *   0  — valid SAIL
 *   1  — validation errors (preview still written)
 *   2  — bad invocation (file missing, etc.)
 */
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

// driver.mjs now ships inside the user-scope plugin appian-toolkit, so its own
// location says nothing about which project is being worked on. The default
// output/ directory is resolved against the caller's working directory instead.
const UNIT_ROOT = process.cwd();

// ---------- argv ----------
const argv = process.argv.slice(2);
let inputPath = null;
let outPath = null;
let noOpen = false;
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--no-open") noOpen = true;
  else if (a === "--out") outPath = argv[++i];
  else if (a === "-h" || a === "--help") {
    console.log("usage: node driver.mjs [file.sail] [--out file.html] [--no-open]");
    process.exit(0);
  } else if (!inputPath) inputPath = a;
  else {
    console.error("Unexpected argument: " + a);
    process.exit(2);
  }
}

// ---------- resolve input ----------
if (!inputPath) {
  const outputDir = path.join(UNIT_ROOT, "output");
  if (!fs.existsSync(outputDir)) {
    console.error("No input given and " + outputDir + " does not exist.");
    process.exit(2);
  }
  const candidates = fs
    .readdirSync(outputDir)
    .filter((f) => f.toLowerCase().endsWith(".sail"))
    .map((f) => path.join(outputDir, f));
  if (candidates.length === 0) {
    console.error("No .sail files in " + outputDir);
    process.exit(2);
  }
  candidates.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
  inputPath = candidates[0];
  console.log("No input given; using newest: " + inputPath);
}
inputPath = path.resolve(inputPath);
if (!fs.existsSync(inputPath)) {
  console.error("File not found: " + inputPath);
  process.exit(2);
}

// ---------- read + tokenize + validate ----------
const src = fs.readFileSync(inputPath, "utf8");
const tokens = tokenize(src);
const report = validate(src, tokens);

// ---------- console report ----------
printReport(report, inputPath);

// ---------- HTML ----------
if (!outPath) outPath = inputPath.replace(/\.sail$/i, "") + ".preview.html";
outPath = path.resolve(outPath);
const html = renderHtml(src, tokens, report, path.basename(inputPath));
fs.writeFileSync(outPath, html);
console.log("\nPreview written: " + outPath);

// ---------- open ----------
if (!noOpen) openInBrowser(outPath);

process.exit(report.ok ? 0 : 1);

// ============================================================
// Tokenizer
// ============================================================
function tokenize(src) {
  const tokens = [];
  const n = src.length;
  let i = 0;
  let line = 1;
  let col = 1;

  function advance(text) {
    for (const ch of text) {
      if (ch === "\n") {
        line++;
        col = 1;
      } else col++;
    }
  }

  while (i < n) {
    const c = src[i];
    const startLine = line;
    const startCol = col;

    // Block comment /* ... */
    if (c === "/" && src[i + 1] === "*") {
      let j = i + 2;
      while (j < n - 1 && !(src[j] === "*" && src[j + 1] === "/")) j++;
      if (j >= n - 1 && !(src[j] === "*" && src[j + 1] === "/")) {
        const text = src.slice(i);
        tokens.push({ type: "comment", value: text, line: startLine, col: startCol, unterminated: true });
        advance(text);
        i = n;
      } else {
        const text = src.slice(i, j + 2);
        tokens.push({ type: "comment", value: text, line: startLine, col: startCol });
        advance(text);
        i = j + 2;
      }
      continue;
    }

    // String "..."  — SAIL escapes a quote by doubling: ""
    if (c === '"') {
      let j = i + 1;
      let closed = false;
      while (j < n) {
        if (src[j] === '"' && src[j + 1] === '"') {
          j += 2;
          continue;
        }
        if (src[j] === '"') {
          closed = true;
          break;
        }
        j++;
      }
      if (!closed) {
        const text = src.slice(i);
        tokens.push({ type: "string", value: text, line: startLine, col: startCol, unterminated: true });
        advance(text);
        i = n;
      } else {
        const text = src.slice(i, j + 1);
        tokens.push({ type: "string", value: text, line: startLine, col: startCol });
        advance(text);
        i = j + 1;
      }
      continue;
    }

    // Identifier — may contain ! as namespace separator (a!foo, local!x, ri!arg)
    if (/[A-Za-z_]/.test(c)) {
      let j = i;
      while (j < n && /[A-Za-z0-9_!]/.test(src[j])) j++;
      const text = src.slice(i, j);
      let type = "identifier";
      const kw = new Set(["true", "false", "null", "if", "and", "or", "not"]);
      if (kw.has(text)) type = "keyword";
      else if (text.includes("!")) type = "namespaced";
      tokens.push({ type, value: text, line: startLine, col: startCol });
      advance(text);
      i = j;
      continue;
    }

    // Number
    if (/[0-9]/.test(c) || (c === "-" && /[0-9]/.test(src[i + 1] || ""))) {
      let j = i + (c === "-" ? 1 : 0);
      while (j < n && /[0-9.]/.test(src[j])) j++;
      const text = src.slice(i, j);
      tokens.push({ type: "number", value: text, line: startLine, col: startCol });
      advance(text);
      i = j;
      continue;
    }

    // Brackets — tracked separately for balance check
    if ("(){}[]".includes(c)) {
      tokens.push({ type: "bracket", value: c, line: startLine, col: startCol });
      advance(c);
      i++;
      continue;
    }

    // Punctuation
    if (",:;".includes(c)) {
      tokens.push({ type: "punct", value: c, line: startLine, col: startCol });
      advance(c);
      i++;
      continue;
    }

    // Whitespace or operator pass-through
    if (/\s/.test(c)) {
      tokens.push({ type: "ws", value: c, line: startLine, col: startCol });
    } else {
      tokens.push({ type: "op", value: c, line: startLine, col: startCol });
    }
    advance(c);
    i++;
  }
  return tokens;
}

// ============================================================
// Validator
// ============================================================
function validate(src, tokens) {
  const issues = [];
  const stack = [];
  const closers = { ")": "(", "}": "{", "]": "[" };
  const openers = new Set(["(", "{", "["]);

  for (const t of tokens) {
    if (t.unterminated && t.type === "comment") {
      issues.push({ severity: "error", line: t.line, msg: "Unterminated block comment (missing */)" });
    }
    if (t.unterminated && t.type === "string") {
      issues.push({ severity: "error", line: t.line, msg: "Unterminated string literal (missing closing \")" });
    }
    if (t.type === "bracket") {
      if (openers.has(t.value)) {
        stack.push({ open: t.value, line: t.line, col: t.col });
      } else {
        const expected = closers[t.value];
        const top = stack.pop();
        if (!top) {
          issues.push({ severity: "error", line: t.line, msg: `Unexpected '${t.value}' — no matching opener` });
        } else if (top.open !== expected) {
          issues.push({
            severity: "error",
            line: t.line,
            msg: `Mismatched '${t.value}' — opener was '${top.open}' at line ${top.line}`,
          });
        }
      }
    }
  }
  while (stack.length) {
    const top = stack.pop();
    issues.push({ severity: "error", line: top.line, msg: `Unclosed '${top.open}' — never matched` });
  }

  // Inventory — counts of namespaced identifiers
  const aFns = new Map();
  const buckets = { local: new Set(), ri: new Set(), recordType: new Set(), rule: new Set(), cons: new Set(), fv: new Set(), index: new Set(), tp: new Set() };
  for (const t of tokens) {
    if (t.type !== "namespaced") continue;
    const ix = t.value.indexOf("!");
    const prefix = t.value.slice(0, ix);
    const name = t.value.slice(ix + 1);
    if (prefix === "a") aFns.set(t.value, (aFns.get(t.value) || 0) + 1);
    else if (buckets[prefix]) buckets[prefix].add(name);
  }

  return {
    ok: issues.filter((i) => i.severity === "error").length === 0,
    issues,
    lines: src.split("\n").length,
    bytes: Buffer.byteLength(src, "utf8"),
    inventory: { a: aFns, ...buckets },
  };
}

// ============================================================
// Console report
// ============================================================
function printReport(r, inputPath) {
  console.log("\n=== SAIL validation ===");
  console.log("File:   " + inputPath);
  console.log("Lines:  " + r.lines);
  console.log("Bytes:  " + r.bytes);
  console.log("Status: " + (r.ok ? "OK" : "FAIL"));
  if (r.issues.length) {
    console.log("\nIssues:");
    for (const i of r.issues) {
      console.log(`  [${i.severity}] line ${i.line}: ${i.msg}`);
    }
  }
  console.log("\nInventory:");
  console.log("  a!* fns (unique): " + r.inventory.a.size);
  const top = [...r.inventory.a.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8);
  for (const [name, count] of top) console.log(`    ${name.padEnd(28)} ${count}`);
  console.log("  local! vars:      " + r.inventory.local.size);
  console.log("  ri! refs:         " + r.inventory.ri.size);
  console.log("  recordType! refs: " + r.inventory.recordType.size);
  console.log("  rule! refs:       " + r.inventory.rule.size);
  if (r.inventory.cons.size) console.log("  cons! refs:       " + r.inventory.cons.size);
  if (r.inventory.fv.size) console.log("  fv! refs:         " + r.inventory.fv.size);
}

// ============================================================
// HTML render
// ============================================================
function renderHtml(src, tokens, report, title) {
  const COLOURS = {
    comment: "#6a9955",
    string: "#ce9178",
    keyword: "#c586c0",
    number: "#b5cea8",
    bracket: "#ffd700",
    punct: "#d4d4d4",
    op: "#d4d4d4",
    a: "#4ec9b0",
    local: "#9cdcfe",
    ri: "#dcdcaa",
    recordType: "#4fc1ff",
    rule: "#c586c0",
    cons: "#569cd6",
    fv: "#9cdcfe",
    index: "#9cdcfe",
    tp: "#9cdcfe",
    identifier: "#d4d4d4",
  };

  let body = "";
  for (const t of tokens) {
    if (t.type === "ws") {
      body += escapeHtml(t.value);
      continue;
    }
    let colour = COLOURS[t.type] || COLOURS.identifier;
    if (t.type === "namespaced") {
      const prefix = t.value.slice(0, t.value.indexOf("!"));
      colour = COLOURS[prefix] || COLOURS.identifier;
    }
    body += `<span style="color:${colour}">${escapeHtml(t.value)}</span>`;
  }

  const lineCount = src.split("\n").length;
  const nums = Array.from({ length: lineCount }, (_, i) => i + 1).join("\n");

  const topA = [...report.inventory.a.entries()].sort((a, b) => b[1] - a[1]).slice(0, 12);
  const aRows = topA.map(([n, c]) => `<tr><td>${escapeHtml(n)}</td><td>${c}</td></tr>`).join("");

  const issuesHtml =
    report.issues.length === 0
      ? '<p style="color:#3fb950;margin:0">No issues found.</p>'
      : "<ul style='margin:0;padding-left:18px'>" +
        report.issues
          .map(
            (i) =>
              `<li style="color:${i.severity === "error" ? "#f85149" : "#dcdcaa"}"><b>line ${i.line}:</b> ${escapeHtml(i.msg)}</li>`
          )
          .join("") +
        "</ul>";

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>SAIL Preview — ${escapeHtml(title)}</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: -apple-system, "Segoe UI", Roboto, sans-serif; background:#1e1e1e; color:#d4d4d4; margin:0; padding:0; }
  header { background:#252526; padding:14px 24px; border-bottom:1px solid #3e3e42; display:flex; align-items:center; gap:18px; flex-wrap:wrap; position:sticky; top:0; z-index:10; }
  header h1 { margin:0; font-size:16px; font-weight:600; }
  header .meta { color:#858585; font-size:12px; }
  header .status { padding:4px 12px; border-radius:4px; font-weight:bold; font-size:12px; letter-spacing:0.05em; }
  header .ok { background:#0e4429; color:#3fb950; }
  header .fail { background:#67060c; color:#f85149; }
  .container { display:grid; grid-template-columns: 1fr 340px; min-height:calc(100vh - 53px); }
  .code { display:grid; grid-template-columns: 64px 1fr; font-family: "Cascadia Code", "JetBrains Mono", Consolas, monospace; font-size:13px; line-height:1.55; overflow:auto; }
  .nums { background:#1e1e1e; color:#858585; text-align:right; padding:14px 10px; user-select:none; white-space:pre; border-right:1px solid #2d2d30; }
  .src { padding:14px 18px; white-space:pre; tab-size:2; overflow-x:auto; }
  .panel { background:#252526; border-left:1px solid #3e3e42; padding:18px 22px; font-size:13px; overflow-y:auto; max-height:calc(100vh - 53px); position:sticky; top:53px; }
  .panel h2 { font-size:11px; margin:18px 0 8px; color:#9d9d9d; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; }
  .panel h2:first-child { margin-top:0; }
  .panel table { width:100%; border-collapse:collapse; }
  .panel td { padding:3px 0; font-family:"Cascadia Code", Consolas, monospace; font-size:12px; }
  .panel td:last-child { text-align:right; color:#858585; }
  .kv { display:flex; justify-content:space-between; padding:3px 0; }
  .kv .v { color:#858585; }
</style>
</head>
<body>
<header>
  <h1>SAIL Preview</h1>
  <span class="meta">${escapeHtml(title)}</span>
  <span class="status ${report.ok ? "ok" : "fail"}">${report.ok ? "VALID" : "INVALID"}</span>
  <span class="meta" style="margin-left:auto">${report.lines} lines · ${report.bytes} bytes</span>
</header>
<div class="container">
  <div class="code">
    <div class="nums">${nums}</div>
    <div class="src">${body}</div>
  </div>
  <aside class="panel">
    <h2>Validation</h2>
    ${issuesHtml}

    <h2>Inventory</h2>
    <div class="kv"><span>Unique a!* fns</span><span class="v">${report.inventory.a.size}</span></div>
    <div class="kv"><span>local! vars</span><span class="v">${report.inventory.local.size}</span></div>
    <div class="kv"><span>ri! refs</span><span class="v">${report.inventory.ri.size}</span></div>
    <div class="kv"><span>recordType! refs</span><span class="v">${report.inventory.recordType.size}</span></div>
    <div class="kv"><span>rule! refs</span><span class="v">${report.inventory.rule.size}</span></div>
    ${report.inventory.cons.size ? `<div class="kv"><span>cons! refs</span><span class="v">${report.inventory.cons.size}</span></div>` : ""}
    ${report.inventory.fv.size ? `<div class="kv"><span>fv! refs</span><span class="v">${report.inventory.fv.size}</span></div>` : ""}

    <h2>Top a!* fns</h2>
    <table>${aRows || '<tr><td colspan="2" style="color:#858585">(none)</td></tr>'}</table>
  </aside>
</div>
</body>
</html>`;
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// ============================================================
// Browser opener
// ============================================================
function openInBrowser(filePath) {
  const platform = process.platform;
  try {
    if (platform === "win32") {
      // start "" "<path>" — empty title arg so paths with spaces work
      spawn("cmd", ["/c", "start", '""', filePath], { detached: true, stdio: "ignore", windowsVerbatimArguments: false }).unref();
    } else if (platform === "darwin") {
      spawn("open", [filePath], { detached: true, stdio: "ignore" }).unref();
    } else {
      spawn("xdg-open", [filePath], { detached: true, stdio: "ignore" }).unref();
    }
    console.log("Opened in default browser.");
  } catch (e) {
    console.error("Could not open browser: " + e.message);
    console.error("Open manually: " + filePath);
  }
}
