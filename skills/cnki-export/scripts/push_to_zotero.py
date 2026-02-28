#!/usr/bin/env python3
"""Push CNKI paper data to Zotero via local Connector API (localhost:23119)."""

import json
import sys
import io
import urllib.request
import urllib.error
import re
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ZOTERO_API = 'http://127.0.0.1:23119/connector'


def zotero_request(endpoint, data=None):
    """Send request to Zotero local API."""
    url = f'{ZOTERO_API}/{endpoint}'
    body = json.dumps(data or {}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={
        'Content-Type': 'application/json',
        'X-Zotero-Connector-API-Version': '3'
    })
    try:
        resp = urllib.request.urlopen(req)
        text = resp.read().decode('utf-8')
        return resp.status, json.loads(text) if text else None
    except urllib.error.HTTPError as e:
        return e.code, None
    except urllib.error.URLError:
        return 0, None


def get_selected_collection():
    """Get currently selected Zotero collection."""
    status, data = zotero_request('getSelectedCollection')
    if status != 200 or not data:
        return None
    return data


def list_collections():
    """List all available Zotero collections."""
    data = get_selected_collection()
    if not data:
        print('Error: 无法连接 Zotero。请确保 Zotero 桌面端已启动。')
        return
    print(f'当前选中分类: {data.get("name", "?")} (ID: {data.get("id", "?")})')
    print(f'文库: {data.get("libraryName", "?")}')
    print()
    print('可用分类:')
    for t in data.get('targets', []):
        indent = '  ' * t.get('level', 0)
        recent = ' *' if t.get('recent') else ''
        print(f'  {indent}{t["name"]} (ID: {t["id"]}){recent}')


def parse_elearning(text):
    """Parse CNKI ELEARNING export format into structured fields."""
    text = text.replace('<br>', '\n').replace('\r', '')
    text = re.sub(r'<[^>]+>', '', text)  # strip HTML tags

    def get(key):
        m = re.search(rf'{re.escape(key)}:\s*(.+?)(?=\n|$)', text)
        return m.group(1).strip() if m else ''

    return {
        'title': get('Title-题名'),
        'authors': [a.strip() for a in get('Author-作者').split(';') if a.strip()],
        'journal': get('Source-刊名'),
        'year': get('Year-年'),
        'pubTime': get('PubTime-出版时间'),
        'keywords': [k.strip() for k in get('Keyword-关键词').split(';') if k.strip()],
        'abstract': get('Summary-摘要'),
        'volume': get('Roll-卷'),
        'issue': get('Period-期'),
        'pageCount': get('PageCount-页数'),
        'pages': get('Page-页码'),
        'organs': get('Organ-机构'),
        'link': get('Link-链接'),
        'srcDb': get('SrcDatabase-来源库'),
    }


def build_zotero_item(paper):
    """Build Zotero item JSON from paper data (matching Zotero Connector output)."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    item = {
        'itemType': 'journalArticle',
        'title': paper.get('title', ''),
        'abstractNote': paper.get('abstract', ''),
        'date': paper.get('pubTime') or paper.get('year', ''),
        'language': 'zh-CN',
        'libraryCatalog': 'CNKI',
        'accessDate': now,
        'volume': paper.get('volume', ''),
        'pages': paper.get('pages', ''),
        'publicationTitle': paper.get('journal', ''),
        'issue': paper.get('issue', ''),
        'creators': [{'name': a, 'creatorType': 'author'} for a in paper.get('authors', [])],
        'tags': [{'tag': k, 'type': 1} for k in paper.get('keywords', [])],
        'attachments': [],
    }

    # URL: use Zotero Connector's format for compatibility
    dbcode = paper.get('dbcode', '')
    dbname = paper.get('dbname', '')
    filename = paper.get('filename', '')
    if dbcode and dbname and filename:
        item['url'] = f'https://kns.cnki.net/KCMS/detail/detail.aspx?dbcode={dbcode}&dbname={dbname}&filename={filename}'
    elif paper.get('link'):
        item['url'] = paper['link']

    # ISSN
    if paper.get('issn'):
        item['ISSN'] = paper['issn']

    # Build extra field (matching Zotero Connector's CNKI translator output)
    extra_parts = []
    if paper.get('journalEN'):
        extra_parts.append(f'original-container-title: {paper["journalEN"]}')
    if paper.get('foundation'):
        extra_parts.append(f'foundation: {paper["foundation"]}')
    if paper.get('downloadCount'):
        extra_parts.append(f'download: {paper["downloadCount"]}')
    if paper.get('album'):
        extra_parts.append(f'album: {paper["album"]}')
    if paper.get('clcCode'):
        extra_parts.append(f'CLC: {paper["clcCode"]}')
    if dbcode:
        extra_parts.append(f'dbcode: {dbcode}')
    if dbname:
        extra_parts.append(f'dbname: {dbname}')
    if filename:
        extra_parts.append(f'filename: {filename}')
    if paper.get('publicationTag'):
        extra_parts.append(f'publicationTag: {paper["publicationTag"]}')
    if paper.get('cif'):
        extra_parts.append(f'CIF: {paper["cif"]}')
    if paper.get('aif'):
        extra_parts.append(f'AIF: {paper["aif"]}')

    if extra_parts:
        item['extra'] = '\n'.join(extra_parts)

    return item


def save_items(items, uri=''):
    """Push items to Zotero via saveItems API."""
    import random
    import string
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    data = {
        'sessionID': session_id,
        'uri': uri,
        'items': items
    }
    status, resp = zotero_request('saveItems', data)
    return status


def main():
    """Main entry point. Accepts JSON paper data from stdin or file argument."""
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_collections()
        return

    # Check Zotero is running
    status, _ = zotero_request('ping')
    if status == 0:
        print('Error: Zotero 未运行。请启动 Zotero 桌面端。')
        sys.exit(1)

    # Show current collection
    col = get_selected_collection()
    if col:
        print(f'Zotero 当前分类: {col.get("name", "?")}')

    # Read paper data from stdin or file
    if len(sys.argv) > 1 and sys.argv[1] != '--list':
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            paper_data = json.load(f)
    else:
        paper_data = json.load(sys.stdin)

    # Handle both single paper and array
    if isinstance(paper_data, list):
        papers = paper_data
    elif 'items' in paper_data:
        # Already in Zotero format
        status = save_items(paper_data['items'], paper_data.get('uri', ''))
        if status == 201:
            print(f'成功添加 {len(paper_data["items"])} 篇论文到 Zotero！')
        else:
            print(f'添加失败，状态码: {status}')
        return
    else:
        papers = [paper_data]

    # Build Zotero items
    items = []
    for p in papers:
        if 'itemType' in p:
            items.append(p)
        elif 'title' in p and 'authors' in p:
            items.append(build_zotero_item(p))
        elif 'ELEARNING' in p:
            parsed = parse_elearning(p['ELEARNING'])
            # Merge page-level fields into parsed data
            for k in ['issn', 'dbcode', 'dbname', 'filename', 'clcCode',
                       'journalEN', 'foundation', 'downloadCount', 'album',
                       'publicationTag', 'cif', 'aif', 'pageUrl']:
                if k in p and p[k]:
                    parsed[k] = p[k]
            items.append(build_zotero_item(parsed))

    if not items:
        print('Error: 无有效论文数据。')
        sys.exit(1)

    uri = papers[0].get('pageUrl', papers[0].get('link', ''))
    status = save_items(items, uri)
    if status == 201:
        print(f'成功添加 {len(items)} 篇论文到 Zotero！')
        for item in items:
            print(f'  - {item.get("title", "?")}')
    else:
        print(f'添加失败，状态码: {status}')
        sys.exit(1)


if __name__ == '__main__':
    main()
