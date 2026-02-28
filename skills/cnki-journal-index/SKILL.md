---
name: cnki-journal-index
description: Query journal indexing/inclusion status on CNKI - check which databases include a journal (北大核心, CSSCI, CSCD, SCI, EI, etc.), get impact factors and evaluation data. Use when user asks about a journal's level, indexing, or ranking.
argument-hint: "[journal name or journal detail URL]"
---

# CNKI Journal Indexing Query (收录查询)

Check which databases index a journal and extract evaluation metrics from its CNKI detail page.

## Arguments

`$ARGUMENTS` is either:
- A journal name (will search first, then navigate to detail)
- A CNKI journal detail URL (containing `navi.cnki.net/knavi/detail`)

## Steps

### 1. Navigate to the journal detail page

**If URL provided:** Navigate directly.
- Use `mcp__chrome-devtools__navigate_page` with the URL.
- Use `mcp__chrome-devtools__wait_for` with text `["该刊被以下数据库收录"]` and timeout 15000.

**If journal name provided:** Search first.
- Navigate to `https://navi.cnki.net/knavi`
- Search for the journal (same as cnki-journal-search steps 2-4)
- Click the first matching journal title link
- Use `mcp__chrome-devtools__list_pages` to find and select the new detail tab
- Wait for the detail page to load

### 2. Check for captcha

Take snapshot. If "拖动下方拼图完成验证" found, notify user.

### 3. Extract journal info via JavaScript

Use `mcp__chrome-devtools__evaluate_script` with this function:

```javascript
() => {
  const body = document.body.innerText;

  // Journal title
  const titleEl = document.querySelector('h3.titbox, h3.titbox1');
  const titleText = titleEl?.innerText?.trim() || '';
  const titleParts = titleText.split('\n').map(s => s.trim()).filter(Boolean);
  const nameCN = titleParts[0] || '';
  const nameEN = titleParts[1] || '';

  // Indexing tags - extract from text between title and "基本信息"
  const tagText = body.match(/Chinese.*?\n\n([\s\S]*?)\n\n基本信息/)?.[1]
    || body.match(new RegExp(nameCN + '[\\s\\S]*?\\n\\n([\\s\\S]*?)\\n\\n基本信息'))?.[1]
    || '';
  const knownTags = ['北大核心','CSSCI','CSCD','SCI','EI','CAS','JST','WJCI','AMI','Scopus','卓越期刊','网络首发'];
  const indexedIn = knownTags.filter(tag => tagText.includes(tag) || body.includes(tag));

  // Basic info
  const sponsor = body.match(/主办单位[：:]\s*(.+?)(?=\n)/)?.[1] || '';
  const frequency = body.match(/出版周期[：:]\s*(\S+)/)?.[1] || '';
  const issn = body.match(/ISSN[：:]\s*(\S+)/)?.[1] || '';
  const cn = body.match(/CN[：:]\s*(\S+)/)?.[1] || '';

  // Publication info
  const collection = body.match(/专辑名称[：:]\s*(.+?)(?=\n)/)?.[1] || '';
  const paperCount = body.match(/出版文献量[：:]\s*(.+?)(?=\n)/)?.[1] || '';

  // Evaluation info
  const impactComposite = body.match(/复合影响因子[：:]\s*([\d.]+)/)?.[1] || '';
  const impactComprehensive = body.match(/综合影响因子[：:]\s*([\d.]+)/)?.[1] || '';

  // "该刊被以下数据库收录" section - click "更多介绍" first if needed
  const moreBtn = Array.from(document.querySelectorAll('a')).find(a => a.innerText?.includes('更多介绍'));
  const hasMoreIntro = !!moreBtn;

  return {
    nameCN,
    nameEN,
    indexedIn,
    sponsor,
    frequency,
    issn,
    cn,
    collection,
    paperCount,
    impactComposite,
    impactComprehensive,
    hasMoreIntro,
    rawTagText: tagText.substring(0, 200)
  };
}
```

### 4. Get detailed indexing info (optional)

If the extraction shows `hasMoreIntro: true`, click the "更多介绍" link to expand detailed indexing information, then take a new snapshot to capture the expanded content.

The expanded section typically lists specific database inclusions with years, such as:
- 北大核心期刊（2023年版）
- CSCD中国科学引文数据库来源期刊（2023-2024年度）
- EI 工程索引（美）

### 5. Check "统计与评价" tab (for detailed metrics)

If the user wants detailed evaluation data:
- Find and click the "统计与评价" link/tab in the snapshot
- Wait for the statistics section to load
- Extract additional metrics (H-index, citation distribution, etc.)

### 6. Present results

```
## {nameCN} ({nameEN})

**收录数据库：** {indexedIn joined by " | "}

**基本信息：**
- ISSN: {issn}
- CN: {cn}
- 主办单位: {sponsor}
- 出版周期: {frequency}
- 专辑: {collection}
- 出版文献量: {paperCount}

**评价指标：**
- 复合影响因子 (2025版): {impactComposite}
- 综合影响因子 (2025版): {impactComprehensive}

**收录情况：**
{For each tag in indexedIn: "- ✓ {tag}"}
```

## Verified Page Structure

The journal detail page (`navi.cnki.net/knavi/detail`) has:

| Data                  | Location                                    |
|-----------------------|---------------------------------------------|
| Title                 | `h3.titbox.titbox1` — first line CN, second line EN |
| Indexing tags         | Text nodes after title: "北大核心", "EI", "CSCD", etc. |
| "被以下数据库收录"    | `h4` heading, below tags                   |
| Basic info            | Text patterns: "主办单位：", "ISSN：", "CN：", "出版周期：" |
| Publication info      | Text patterns: "专辑名称：", "出版文献量：" |
| Evaluation info       | Text patterns: "复合影响因子：", "综合影响因子：" |
| Detailed indexing     | Expandable via "更多介绍" link              |
| Stats tab             | "统计与评价" tab link                       |
| Detail page opens in  | **New tab** — use list_pages + select_page  |

## Common Indexing Databases

| Tag       | Full Name                                    |
|-----------|----------------------------------------------|
| 北大核心   | 北京大学中文核心期刊                          |
| CSSCI     | 中文社会科学引文索引                          |
| CSCD      | 中国科学引文数据库                            |
| SCI       | Science Citation Index                       |
| EI        | Engineering Index                            |
| CAS       | Chemical Abstracts Service                   |
| JST       | Japan Science and Technology Agency          |
| WJCI      | World Journal Clout Index                    |
| AMI       | 中国人文社会科学期刊 AMI 综合评价             |
| Scopus    | Elsevier Scopus                              |
