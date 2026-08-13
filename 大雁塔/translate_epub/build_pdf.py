# -*- coding: utf-8 -*-
# build_pdf.py - 双语对照 PDF 生成器 (HTML + Edge headless)
# 用法: python build_pdf.py [--orientation landscape|portrait] [--size A4|B5|A5] [--chapter N]
import sys, io, json, html, subprocess, os, argparse
from pathlib import Path
if sys.stdout.encoding and sys.stdout.encoding.lower().startswith('gbk'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = sys.stdout
OUTPUT_DIR = Path(r'D:\personalprofile\电子书\大雁塔\translate_epub\output')
PROGRESS_FILE = OUTPUT_DIR / 'progress.json'
HTML_PATH = OUTPUT_DIR / 'bilingual.html'

STYLE = (
    '@font-face { font-family: "Source Han Serif SC", "Songti SC", "SimSun", serif; }' +
    '@page { size: ' + chr(123) + 'size' + chr(125) + ' ' + chr(123) + 'orientation' + chr(125) + '; margin: 1.2cm; }' +
    'body { margin: 0; font-size: 10pt; line-height: 1.7; }' +
    '.container { display: flex; gap: 1cm; }' +
    '.col { flex: 1; min-width: 0; overflow-wrap: break-word; }' +
    '.col-en { color: #555; }' +
    '.col-zh { color: #000; padding-left: 0.6cm; border-left: 1px solid #ccc; }' +
    'h1 { font-size: 16pt; text-align: center; margin: 0 0 0.6em; font-weight: bold; }' +
    'p { margin: 0 0 0.5em 0; text-align: justify; text-indent: 1.2em; }' +
    '.page-break { page-break-after: always; height: 0; }'
)


def build_html(progress, orientation='landscape', size='B5', only_cid=None):
    style = STYLE.replace("{size}", size).replace("{orientation}", orientation)
    parts = [f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{style}</style></head><body>']
    cids = [only_cid] if only_cid else sorted(progress.keys())
    for cid in cids:
        ch = progress.get(cid)
        if not ch: continue
        items = ch.get('items', [])
        title = ch.get('title') or cid
        if not items: continue
        parts.append('<h1>' + html.escape(str(title)) + '</h1>')
        parts.append('<div class="container">')
        parts.append('<div class="col col-en">')
        for it in items:
            txt = it['original'].replace(chr(10), ' ').strip()
            if txt: parts.append('<p>' + html.escape(txt) + '</p>')
        parts.append('</div>')
        parts.append('<div class="col col-zh">')
        for it in items:
            txt = it['translation'].replace(chr(10), ' ').strip()
            if txt: parts.append('<p>' + html.escape(txt) + '</p>')
        parts.append('</div>')
        parts.append('</div>')
        parts.append('<div class="page-break"></div>')
    parts.append('</body></html>')
    return chr(10).join(parts)

def find_browser():
    candidates = [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe'),
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    ]
    for p in candidates:
        if Path(p).exists(): return p
    return None

def html_to_pdf(html_path, pdf_path):
    browser = find_browser()
    if not browser: raise RuntimeError('No Edge/Chrome found')
    print('browser:', browser)
    subprocess.run([browser, '--headless=new', '--disable-gpu', '--no-sandbox', '--print-to-pdf=' + str(pdf_path), '--no-pdf-header-footer', '--virtual-time-budget=10000', str(html_path)], check=True, timeout=300)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--orientation', default='landscape', choices=['landscape','portrait'])
    ap.add_argument('--size', default='B5', choices=['A4','B5','A5'])
    ap.add_argument('--chapter', type=int, default=None, help='只生成指定章节')
    ap.add_argument('--html-only', action='store_true')
    a = ap.parse_args()
    if not PROGRESS_FILE.exists():
        print('No progress.json'); return
    progress = json.loads(PROGRESS_FILE.read_text(encoding='utf-8'))
    only = None
    if a.chapter is not None:
        for cid in progress:
            if cid.startswith('%02d' % a.chapter): only = cid; break
    print('chapter:', only or 'all')
    html_content = build_html(progress, a.orientation, a.size, only)
    HTML_PATH.write_text(html_content, encoding='utf-8')
    print('HTML:', HTML_PATH, len(html_content), 'bytes')
    if a.html_only: return
    suffix = '_' + a.orientation + '_' + a.size + ('_' + only if only else '')
    pdf_path = OUTPUT_DIR / ('bilingual' + suffix + '.pdf')
    html_to_pdf(HTML_PATH, pdf_path)
    print('PDF:', pdf_path, pdf_path.stat().st_size, 'bytes')

if __name__ == '__main__':
    main()
