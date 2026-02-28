---
name: cnki-download
description: Download a paper PDF/CAJ from CNKI. Requires user to be logged in. Use when user wants to download a specific paper.
argument-hint: "[paper URL or blank if already on detail page]"
---

# CNKI Paper Download (文献下载)

## Prerequisites

User **must be logged in** to CNKI with download permissions.

## Arguments

`$ARGUMENTS` is optionally a paper detail URL. If blank, uses current page.

## Steps

### 1. Navigate (if URL provided)

If URL provided: use `navigate_page` to go to the URL directly (no wait_for needed — Step 2 handles waiting).

**Important**: Always use `navigate_page` instead of clicking links on the search results page. Clicking opens a new tab and wastes 3 extra tool calls (`list_pages` + `select_page` + `take_snapshot`).

### 2. Check status and download (single async evaluate_script)

Replace `FORMAT` with `"pdf"` or `"caj"`:

```javascript
async () => {
  // Wait for page load
  await new Promise((r, j) => {
    let n = 0;
    const c = () => {
      if (document.querySelector('.brief h1')) r();
      else if (++n > 30) j('timeout');
      else setTimeout(c, 500);
    };
    c();
  });

  // Captcha check
  const cap = document.querySelector('#tcaptcha_transform_dy');
  if (cap && cap.getBoundingClientRect().top >= 0) {
    return { error: 'captcha', message: 'CNKI 正在显示滑块验证码。请在 Chrome 中手动完成拼图验证。' };
  }

  const format = "FORMAT"; // "pdf" or "caj"

  // Check download links
  const pdfLink = document.querySelector('#pdfDown') || document.querySelector('.btn-dlpdf a');
  const cajLink = document.querySelector('#cajDown') || document.querySelector('.btn-dlcaj a');

  // Check login status
  const notLogged = document.querySelector('.downloadlink.icon-notlogged')
    || document.querySelector('[class*="notlogged"]');
  if (notLogged) {
    return { error: 'not_logged_in', message: '下载需要登录。请先在 Chrome 中登录知网账号。' };
  }

  const title = document.querySelector('.brief h1')?.innerText?.trim()?.replace(/\s*网络首发\s*$/, '') || '';

  if (format === 'pdf' && pdfLink) {
    pdfLink.click();
    return { status: 'downloading', format: 'PDF', title };
  } else if (format === 'caj' && cajLink) {
    cajLink.click();
    return { status: 'downloading', format: 'CAJ', title };
  } else if (pdfLink) {
    pdfLink.click();
    return { status: 'downloading', format: 'PDF', title };
  } else if (cajLink) {
    cajLink.click();
    return { status: 'downloading', format: 'CAJ', title };
  }

  return { error: 'no_download', message: '未找到下载链接', hasPDF: !!pdfLink, hasCAJ: !!cajLink };
}
```

### 3. Report

Based on JS result:
- `status: downloading` → "PDF 下载已触发：{title}。请在 Chrome 下载管理器中查看。"
- `error: not_logged_in` → tell user to log in
- `error: captcha` → tell user to solve captcha

## Tool calls: 1–2 (navigate_page if URL + evaluate_script)

## Verified selectors

| Element | Selector | Notes |
|---------|----------|-------|
| PDF download | `#pdfDown` | `<a>` inside `li.btn-dlpdf` |
| CAJ download | `#cajDown` | `<a>` inside `li.btn-dlcaj` |
| Download area | `.download-btns` | parent `<div>` |
| Not logged in | `.downloadlink.icon-notlogged` | |
| Title | `.brief h1` | strip trailing "网络首发" |

## Captcha detection

Check `#tcaptcha_transform_dy` element's `getBoundingClientRect().top >= 0`.
Only active when `top >= 0` (visible). Pre-loaded SDK sits at `top: -1000000px`.
