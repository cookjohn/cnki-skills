# CNKI Skills for Claude Code

[English](#english) | [中文](#中文)

| WeChat Official Account (公众号) | WeChat Group (微信群) | Discord |
|:---:|:---:|:---:|
| <img src="qrcode_for_gh_a1c14419b847_258.jpg" width="200"> | <img src="0320.jpg" width="200"> | [Join Discord](https://discord.gg/tGd5vTDASg) |
| 未来论文实验室 | 扫码加入交流群 | English & Chinese |

---

<a id="english"></a>

## English

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills that let Claude interact with [CNKI (中国知网)](https://www.cnki.net) through Chrome DevTools MCP.

Search papers, browse journals, check indexing status, download PDFs, and export to Zotero — all from the Claude Code CLI.

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- Chrome browser (login handled manually for downloads)
- [Zotero](https://www.zotero.org/) desktop app (optional, for export)
- Python 3 (optional, for Zotero push script)

### Skills

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

### Agent

**`cnki-researcher`** — orchestrates all 10 skills. Handles captcha detection (pauses and asks user to solve manually), tab management, and multi-step workflows like "search → filter → export to Zotero".

### Installation

#### 1. Install Chrome DevTools MCP server

```bash
claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest
```

#### 2. Install CNKI skills

```bash
git clone https://github.com/cookjohn/cnki-skills.git
cd cnki-skills
cp -r skills/ agents/ .claude/
```

Or add to an existing project:

```bash
git clone https://github.com/cookjohn/cnki-skills.git /tmp/cnki-skills
cp -r /tmp/cnki-skills/skills/ your-project/.claude/skills/
cp -r /tmp/cnki-skills/agents/ your-project/.claude/agents/
```

#### 3. Start Chrome with remote debugging

```bash
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222
```

#### 4. Launch Claude Code

```bash
claude
```

Skills and agent are picked up automatically. Try `/cnki-search 深度学习` to verify.

### How It Works

All skills use async `evaluate_script` calls via Chrome DevTools MCP — no screenshot parsing or OCR. Each skill operates in 1-2 tool calls (navigate + evaluate_script), making interactions fast and reliable.

Key design choices:
- **Single async script per operation** — replaces multi-step snapshot → click → wait_for patterns
- **`navigate_page` over link clicking** — CNKI opens links in new tabs; navigating directly avoids tab management overhead
- **Batch export** — export multiple papers from search results in one call instead of visiting each detail page
- **Captcha-aware** — detects Tencent slider captcha and pauses for manual resolution

### Project Structure

```
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
agents/
└── cnki-researcher.md              # Agent: orchestrates all skills
```

---

<a id="中文"></a>

## 中文

| 公众号 | 微信交流群 | Discord |
|:---:|:---:|:---:|
| <img src="qrcode_for_gh_a1c14419b847_258.jpg" width="200"> | <img src="0320.jpg" width="200"> | [加入 Discord](https://discord.gg/tGd5vTDASg) |
| 未来论文实验室 | 扫码加入交流群 | 中英文交流 |

让 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 通过 Chrome DevTools MCP 操作 [中国知网 (CNKI)](https://www.cnki.net) 的技能集。

支持论文检索、期刊浏览、收录查询、PDF 下载、导出到 Zotero 等功能，全部在 Claude Code 命令行中完成。

### 前置要求

- 已安装 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Chrome 浏览器（下载功能需手动登录知网）
- [Zotero](https://www.zotero.org/) 桌面端（可选，用于导出）
- Python 3（可选，用于 Zotero 推送脚本）

### 技能列表

| 技能 | 功能 | 调用方式 |
|------|------|----------|
| `cnki-search` | 关键词检索，返回结构化结果 | `/cnki-search 人工智能` |
| `cnki-advanced-search` | 高级检索：作者、期刊、时间、来源类别（SCI/EI/CSSCI/北大核心/CSCD） | `/cnki-advanced-search CSSCI 人工智能 2020-2025` |
| `cnki-parse-results` | 重新解析当前搜索结果页 | `/cnki-parse-results` |
| `cnki-navigate-pages` | 翻页与排序 | `/cnki-navigate-pages next` |
| `cnki-paper-detail` | 提取论文详细信息（摘要、关键词等） | `/cnki-paper-detail` |
| `cnki-journal-search` | 按名称、ISSN、CN 号查找期刊 | `/cnki-journal-search 计算机学报` |
| `cnki-journal-index` | 查询期刊收录情况和影响因子 | `/cnki-journal-index 计算机学报` |
| `cnki-journal-toc` | 浏览期刊目录 | `/cnki-journal-toc 计算机学报 2025 01期` |
| `cnki-download` | 下载论文 PDF/CAJ | `/cnki-download` |
| `cnki-export` | 推送到 Zotero 或输出 GB/T 7714 引用 | `/cnki-export zotero` |

### 智能体

**`cnki-researcher`** — 统一调度全部 10 个技能。自动处理验证码检测（暂停并提示用户手动完成）、标签页管理，支持"检索 → 筛选 → 导出到 Zotero"等复合工作流。

### 安装方法

#### 1. 安装 Chrome DevTools MCP 服务器

```bash
claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest
```

#### 2. 安装 CNKI 技能

```bash
git clone https://github.com/cookjohn/cnki-skills.git
cd cnki-skills
cp -r skills/ agents/ .claude/
```

添加到已有项目：

```bash
git clone https://github.com/cookjohn/cnki-skills.git /tmp/cnki-skills
cp -r /tmp/cnki-skills/skills/ your-project/.claude/skills/
cp -r /tmp/cnki-skills/agents/ your-project/.claude/agents/
```

#### 3. 启动 Chrome 远程调试

```bash
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222
```

#### 4. 启动 Claude Code

```bash
claude
```

技能和智能体会自动加载。输入 `/cnki-search 深度学习` 验证是否正常。

### 工作原理

所有技能通过 Chrome DevTools MCP 的 `evaluate_script` 异步执行 JavaScript，无需截图识别或 OCR。每个操作仅需 1-2 次工具调用（导航 + 执行脚本），快速且稳定。

核心设计：
- **单次异步脚本** — 取代多步骤的 snapshot → click → wait_for 模式
- **直接导航优于点击链接** — 知网链接会打开新标签页，直接导航避免标签页管理开销
- **批量导出** — 从搜索结果页一次性导出多篇论文，无需逐篇进入详情页
- **验证码感知** — 检测到腾讯滑块验证码时自动暂停，等待用户手动处理

---

## License

MIT
