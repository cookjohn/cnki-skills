---
name: cnki-journal-toc
description: Browse journal issues, view table of contents, and download original TOC PDF from CNKI. Use when user wants to see papers in a specific journal issue or download the original cover/TOC pages.
argument-hint: "[journal name] [year] [issue] [download]"
---

# CNKI Journal Table of Contents (期刊目录浏览 + 原版目录下载)

Browse journal issues, extract the paper list, and optionally open/download the original TOC PDF (封面+目录扫描版).

## Arguments

`$ARGUMENTS` describes what to browse:
- `{journal name}` — which journal
- `{year}` (optional) — which year, defaults to latest
- `{issue}` (optional) — which issue number
- `download` (optional) — if included, download the original TOC PDF

Examples:
- `计算机学报 2026 01期` — browse 2026 issue 1
- `计算机学报 2026 01期 download` — download original TOC PDF
- `计算机学报` — shows latest (网络首发)

## Steps

### 1. Navigate to journal detail page

If not already on a journal detail page (`navi.cnki.net/knavi/detail`):
- Use `cnki-journal-search` to find the journal
- Use `mcp__chrome-devtools__list_pages` + `mcp__chrome-devtools__select_page` to switch to the journal detail tab (opens in new tab)

### 2. Select issue + extract papers (single async evaluate_script)

Replace `YEAR` and `ISSUE` with actual values (e.g., `"2025"`, `"No.01"`).
The "刊期浏览" tab is the default active view — no need to click it.

```javascript
async () => {
  const year = "YEAR";
  const issue = "ISSUE"; // Format: "No.01", "No.12", etc.

  const dls = document.querySelectorAll('#yearissue0 dl.s-dataList');
  let target = null;
  for (const dl of dls) {
    if (dl.querySelector('dt')?.innerText?.trim() === year) {
      target = Array.from(dl.querySelectorAll('dd a')).find(a => a.innerText.trim() === issue);
      break;
    }
  }
  if (!target) {
    // Return available years and issues for the requested year
    const available = Array.from(dls).map(dl => ({
      year: dl.querySelector('dt')?.innerText?.trim(),
      issues: Array.from(dl.querySelectorAll('dd a')).map(a => a.innerText.trim())
    })).filter(y => y.year);
    return { error: 'issue_not_found', year, issue, available: available.slice(0, 5) };
  }

  target.click();

  // Wait for paper list to load
  await new Promise((r, j) => {
    let n = 0;
    const c = () => {
      const rows = document.querySelectorAll('#CataLogContent dd.row');
      if (rows.length > 0) r();
      else if (++n > 30) j('timeout');
      else setTimeout(c, 500);
    };
    setTimeout(c, 1000);
  });

  // Extract papers
  const rows = document.querySelectorAll('#CataLogContent dd.row');
  const papers = Array.from(rows).map((dd, i) => ({
    no: i + 1,
    title: dd.querySelector('span.name a')?.innerText?.trim(),
    authors: dd.querySelector('span.author')?.innerText?.trim()?.replace(/;$/, ''),
    pages: dd.querySelector('span.company')?.innerText?.trim()
  }));

  // Get 原版目录 URL
  const tocBtn = document.querySelector('a.btn-preview:not(.btn-back)');

  return {
    issueLabel: document.querySelector('span.date-list')?.innerText?.trim(),
    paperCount: papers.length,
    papers,
    tocUrl: tocBtn?.href || null,
    url: location.href
  };
}
```

### 3. Present results

```
## {journal_name} — {issueLabel}

共 {paperCount} 篇论文：

1. {title}  [pp. {pages}]
   作者：{authors}

2. {title}  [pp. {pages}]
   作者：{authors}
...
```

### 4. Download original TOC PDF (if requested)

If user requested download, or asks for "原版目录":

**Method A — Click "原版目录浏览" to open reader, then download:**

1. Find the `link` with text "原版目录浏览" in the snapshot (class `btn-preview`)
2. Click it — this opens a new tab with the reader page (`kns.cnki.net/reader/report`)
3. Use `mcp__chrome-devtools__list_pages` to find the new reader tab
4. Use `mcp__chrome-devtools__select_page` to switch to it
5. Use `mcp__chrome-devtools__wait_for` with text `["下载"]`
6. Take snapshot — find the `link` with text "下载" (the download button in the reader toolbar)
7. Click the download link — triggers PDF download via Chrome

**Method B — Direct download from reader page:**

If already on a reader page (`kns.cnki.net/reader/report`):
1. Take snapshot
2. Find `link` with text "下载"
3. Click it

After clicking, inform the user:
> 原版目录 PDF 下载已触发，请在 Chrome 下载管理器中查看。

## Tool calls

- Browse issue: 1 (evaluate_script only) — after navigating to journal page
- Download TOC: requires snapshot + click + tab switching (new tab)

## Verified selectors

### Journal Detail — 刊期浏览

| Element | Selector | Notes |
|---------|----------|-------|
| 刊期浏览 tab | `a` text "刊期浏览" | default active (`li.on.cur`), no need to click |
| Year area | `#yearissue0` / `.yearissuepage` | |
| Year groups | `dl.s-dataList` | inside `#yearissue0` |
| Year label | `dl.s-dataList dt` | text "2026", "2025" etc. |
| Issue links | `dl.s-dataList dd a` | text "No.01", "No.12" etc. |
| Issue label | `span.date-list` | text "2025年01期" |
| Paper container | `#CataLogContent` | |
| Paper entries | `#CataLogContent dd.row` | |
| Paper title | `dd.row span.name a` | href to `kcms2/article/abstract` |
| Paper authors | `dd.row span.author` | semicolon-separated |
| Paper page range | `dd.row span.company` | class is "company" but holds page range |
| Paper ID | `dd.row b[name="encrypt"]` | id like "JSJX202512001" |
| 原版目录浏览 | `a.btn-preview:not(.btn-back)` | href to `bar.cnki.net/bar/download/order` |
| 返回 | `a.btn-preview.btn-back` | |

### Reader Page (kns.cnki.net/reader/report)

| Element | Pattern |
|---------|--------|
| Page title | `RootWebArea "期刊原版目录"` |
| Download button | `link` text "下载", URL to `bar.cnki.net/bar/download/order` |
| Current page | `textbox` value (page number) |
| Total pages | `StaticText` (e.g., "4") |
| Navigation | `generic` description "上一页" / "下一页" |

## Important Notes

- "原版目录浏览" only appears when a **specific issue** is selected (not for 网络首发 view).
- The reader page opens in a **new tab**.
- The download link in the reader requires login. If download fails, remind user to log in.
- The download URL is session-specific — do not cache or reuse.
