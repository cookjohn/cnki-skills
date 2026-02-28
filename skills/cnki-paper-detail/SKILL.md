---
name: cnki-paper-detail
description: Extract full paper details from a CNKI paper page including title, authors, affiliations, abstract, keywords, fund, classification. Use when the user needs detailed information about a specific paper.
argument-hint: "[paper URL or blank if already on detail page]"
---

# CNKI Paper Detail Extraction

Extract complete metadata from a CNKI paper detail page.

## Arguments

`$ARGUMENTS` is optionally a CNKI paper detail URL (containing `kcms2/article/abstract`). If not provided, assumes the current page is already a paper detail page.

## Steps

### 1. Navigate to the paper page (if URL provided)

If `$ARGUMENTS` contains a URL:
- Use `mcp__chrome-devtools__navigate_page` with the URL.
- Use `mcp__chrome-devtools__wait_for` with text `["摘要"]` and timeout 15000.

### 2. Check for captcha

Use `mcp__chrome-devtools__take_snapshot`. If "拖动下方拼图完成验证" found, notify user:

> CNKI 正在显示滑块验证码。请在 Chrome 浏览器中手动完成拼图验证，完成后告诉我继续。

### 3. Extract paper metadata via JavaScript

Use `mcp__chrome-devtools__evaluate_script` with this function:

```javascript
() => {
  const brief = document.querySelector('.brief');
  if (!brief) return { error: 'Paper detail section (.brief) not found' };

  // Title
  const title = brief.querySelector('h1')?.innerText?.trim()
    ?.replace(/\s*附视频\s*$/, '')  // remove "附视频" suffix
    ?.replace(/\s*网络首发\s*$/, ''); // remove "网络首发" suffix

  // Authors - first h3.author contains author links with sup tags
  const authorH3s = brief.querySelectorAll('h3.author');
  const authorSection = authorH3s[0];
  const authors = [];
  if (authorSection) {
    const authorLinks = authorSection.querySelectorAll('a');
    authorLinks.forEach(a => {
      const name = a.innerText?.replace(/\d+$/, '').trim();
      const supMatch = a.innerText?.match(/(\d+)$/);
      const affiliationNum = supMatch ? supMatch[1] : '';
      authors.push({ name, affiliationNum });
    });
  }

  // Affiliations - second h3.author contains org links
  const affiliations = [];
  if (authorH3s.length > 1) {
    const orgLinks = authorH3s[1].querySelectorAll('a');
    orgLinks.forEach(a => {
      affiliations.push(a.innerText?.trim());
    });
  }

  // Abstract
  const abstractEl = document.querySelector('.abstract-text');
  const abstract = abstractEl?.innerText?.trim() || '';

  // Keywords
  const keywordsP = document.querySelector('p.keywords');
  const keywords = keywordsP
    ? Array.from(keywordsP.querySelectorAll('a')).map(a => a.innerText?.replace(/;$/, '').trim())
    : [];

  // Fund
  const fundsP = document.querySelector('p.funds');
  const fund = fundsP?.innerText?.trim() || '';

  // Classification code
  const clcCode = document.querySelector('.clc-code');
  const classification = clcCode?.innerText?.trim() || '';

  // Journal/source
  const docTop = document.querySelector('.doc-top');
  const journal = docTop?.querySelector('a')?.innerText?.trim() || '';

  // Online first / publication info
  const headTime = document.querySelector('.head-time');
  const pubInfo = headTime?.innerText?.trim() || '';

  // Is online first?
  const isOnlineFirst = !!brief.querySelector('.icon-shoufa');

  // Article outline/TOC
  const catalogList = document.querySelector('.catalog-list, .catalog-listDiv');
  const toc = catalogList?.innerText?.trim() || '';

  // Citation network counts
  const citationTabs = document.querySelectorAll('ul.module-tab.tpl_lieteratures li');
  const citationInfo = {};
  citationTabs.forEach(li => {
    const id = li.getAttribute('data-id');
    const text = li.innerText?.trim();
    const countMatch = text.match(/(\d+)/);
    if (id) {
      citationInfo[id] = {
        label: text.replace(/\d+/, '').trim(),
        count: countMatch ? parseInt(countMatch[1]) : 0
      };
    }
  });

  return {
    title,
    authors,
    affiliations,
    abstract,
    keywords,
    fund,
    classification,
    journal,
    pubInfo,
    isOnlineFirst,
    toc,
    citationInfo
  };
}
```

### 4. Format and present the output

```
## {title} {isOnlineFirst ? "[网络首发]" : ""}

**Authors:**
{For each author: "- {name} ({affiliation})"}

**Affiliations:**
{For each affiliation: "- {affiliation}"}

**Journal:** {journal}
**Publication Info:** {pubInfo}

**Abstract:**
{abstract}

**Keywords:** {keywords joined by ", "}

**Fund:** {fund}
**Classification:** {classification}

**Citation Network:**
{For each citation type: "- {label}: {count}"}
```

### 5. Fallback: snapshot-based parsing

If JS extraction fails, use `mcp__chrome-devtools__take_snapshot` and parse the accessibility tree:
- **Title**: `heading` level 1 element
- **Authors**: `link` elements whose URLs contain `kcms2/author/detail`
- **Affiliations**: `link` elements whose URLs contain `kcms2/organ/detail`
- **Abstract**: `StaticText` following "摘要："
- **Keywords**: `link` elements whose URLs contain `kcms2/keyword/detail`
- **Fund**: `link` elements following "基金资助："
- **Classification**: `StaticText` following "分类号："

## Verified DOM Selectors

| Data           | Selector                                   | Notes                                    |
|----------------|--------------------------------------------|------------------------------------------|
| Paper section  | `.brief`                                    | Main paper info container                |
| Title          | `.brief h1`                                 | May contain icons, clean text needed     |
| Authors        | `.brief h3.author:first-of-type a`          | Text has superscript numbers (e.g., "张三1") |
| Affiliations   | `.brief h3.author:nth-of-type(2) a`         | Text starts with "N." (e.g., "1.北京大学") |
| Abstract       | `.abstract-text`                            | Full abstract text                       |
| Keywords       | `p.keywords a`                              | Semicolon-separated keyword links        |
| Fund           | `p.funds`                                   | Fund information text                    |
| Classification | `.clc-code`                                 | CLC classification codes                |
| Journal        | `.doc-top a`                                | Source journal link                      |
| Online first   | `.brief .icon-shoufa`                       | Present if paper is online first         |
| Citation tabs  | `ul.module-tab.tpl_lieteratures li`         | data-id attr identifies type             |
