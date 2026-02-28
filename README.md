# CNKI Skills for Claude Code

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills that let Claude interact with [CNKI (中国知网)](https://www.cnki.net) through Chrome DevTools MCP.

Search papers, browse journals, check indexing status, download PDFs, and export to Zotero — all from the Claude Code CLI.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- [Chrome DevTools MCP server](https://github.com/nicobailon/chrome-devtools-mcp) configured in Claude Code
- Chrome browser with a CNKI session (login handled manually for downloads)
- [Zotero](https://www.zotero.org/) desktop app (optional, for export)
- Python 3 (optional, for Zotero push script)

## Skills

| Skill | Description | Invocation |
|-------|-------------|------------|
| `cnki-search` | Keyword search with structured result extraction | `/cnki-search 人工智能` |
| `cnki-advanced-search` | Filtered search: author, journal, date, source category (SCI/EI/CSSCI/北大核心/CSCD) | `/cnki-advanced-search CSSCI 人工智能 2020-2025` |
| `cnki-parse-results` | Re-parse an existing search results page | `/cnki-parse-results` |
| `cnki-navigate-pages` | Pagination and sort order | `/cnki-navigate-pages next` |
| `cnki-paper-detail` | Extract full paper metadata (abstract, keywords, etc.) | `/cnki-paper-detail` |
| `cnki-journal-search` | Find journals by name, ISSN, or CN | `/cnki-journal-search 计算机学报` |
| `cnki-journal-index` | Check journal indexing status and impact factors | `/cnki-journal-index 计算机学报` |
| `cnki-journal-toc` | Browse issue table of contents | `/cnki-journal-toc 计算机学报 2025 01期` |
| `cnki-download` | Download paper PDF/CAJ | `/cnki-download` |
| `cnki-export` | Push to Zotero or output GB/T 7714 citation | `/cnki-export zotero` |

## Agent

**`cnki-researcher`** — orchestrates all 10 skills. Handles captcha detection (pauses and asks user to solve manually), tab management, and multi-step workflows like "search → filter → export to Zotero".

## Installation

1. Clone this repo:

```bash
git clone https://github.com/cookjohn/cnki-skills.git
```

2. Copy `skills/` and `agents/` into your project's `.claude/` directory:

```bash
cp -r cnki-skills/skills/ your-project/.claude/skills/
cp -r cnki-skills/agents/ your-project/.claude/agents/
```

3. Launch Claude Code in your project:

```bash
cd your-project
claude
```

The skills and agent will be picked up automatically.

### Chrome DevTools MCP

Add to your Claude Code MCP config (`~/.claude/mcp.json` or project-level):

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/chrome-devtools-mcp@latest"]
    }
  }
}
```

Make sure Chrome is running with remote debugging enabled:

```bash
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

## How It Works

All skills use async `evaluate_script` calls via Chrome DevTools MCP — no screenshot parsing or OCR. Each skill operates in 1-2 tool calls (navigate + evaluate_script), making interactions fast and reliable.

Key design choices:
- **Single async script per operation** — replaces multi-step snapshot → click → wait_for patterns
- **`navigate_page` over link clicking** — CNKI opens links in new tabs; navigating directly avoids tab management overhead
- **Batch export** — export multiple papers from search results in one call instead of visiting each detail page
- **Captcha-aware** — detects Tencent slider captcha and pauses for manual resolution

## Project Structure

```
agents/
└── cnki-researcher.md              # Agent: orchestrates all skills
skills/
├── cnki-search/SKILL.md            # Basic keyword search
├── cnki-advanced-search/SKILL.md   # Filtered search (source category, date, etc.)
├── cnki-parse-results/SKILL.md     # Parse existing results page
├── cnki-navigate-pages/SKILL.md    # Pagination & sorting
├── cnki-paper-detail/SKILL.md      # Paper metadata extraction
├── cnki-journal-search/SKILL.md    # Journal lookup
├── cnki-journal-index/SKILL.md     # Journal indexing & impact factors
├── cnki-journal-toc/SKILL.md       # Issue table of contents
├── cnki-download/SKILL.md          # PDF/CAJ download
└── cnki-export/                    # Citation export & Zotero
    ├── SKILL.md
    └── scripts/
        └── push_to_zotero.py       # Zotero Connector API client
```

## License

MIT
