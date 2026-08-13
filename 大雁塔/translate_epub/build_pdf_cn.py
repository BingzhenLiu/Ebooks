# -*- coding: utf-8 -*-
# build_pdf_cn.py - 独立中文译本 PDF (B5 纵向，含图，正式书籍风格)
import sys, io, os, json, html, subprocess, argparse
from pathlib import Path
if sys.stdout.encoding and sys.stdout.encoding.lower().startswith('gbk'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = sys.stdout
OUT = Path(r'D:\personalprofile\电子书\大雁塔\translate_epub\output')
PROG = OUT / 'progress.json'
IMGS = OUT / 'images'
COVER = IMGS / 'cover.jpg'
HTML = OUT / 'cn.html'
PDF = OUT / 'cn_B5_portrait.pdf'

STYLE_CSS = (
    '@font-face { font-family: "F1"; src: local("Source Han Serif SC"), local("Songti SC"), local("SimSun"), serif; }' +
    '@font-face { font-family: "F2"; src: local("Source Han Sans SC"), local("Heiti SC"), local("Microsoft YaHei"), sans-serif; }'
)
PAGE_CSS = (
    '@page { size: __SIZE__ __ORIENT__; margin: 1.6cm 1.4cm 1.8cm 1.4cm; }' +
    '@top-center { content: string(book-title); font-family: F2; font-size: 9pt; color: #888; }' +
    '@bottom-center { content: counter(page); font-size: 10pt; color: #666; }'
)
BODY_CSS = (
    'body { font-family: F1, serif; font-size: 11pt; line-height: 1.85; text-align: justify; }' +
    'h1.chapter-title { font-family: F2, sans-serif; font-size: 22pt; text-align: center; margin: 1em 0 0.8em; page-break-before: always; }' +
    'h2.section { font-family: F2, sans-serif; font-size: 16pt; text-align: center; margin: 1em 0 0.6em; }' +
    'p { margin: 0 0 0.4em 0; text-indent: 2em; }' +
    'p.center { text-align: center; text-indent: 0; }' +
    'p.no-indent { text-indent: 0; }' +
    '.cover-page { page-break-after: always; text-align: center; padding: 0; margin: 0; }' +
    '.cover-page img { max-width: 100%; max-height: 100vh; }' +
    '.title-page { page-break-after: always; text-align: center; padding-top: 25%; }' +
    '.translator-note { font-size: 9pt; color: #666; margin-top: 4em; text-indent: 0; line-height: 1.6; }' +
    '.toc-page { page-break-after: always; padding-top: 1em; }' +
    '.toc-page h2 { font-size: 20pt; margin-bottom: 1em; }' +
    '.toc-list { list-style: none; padding-left: 0; }' +
    '.toc-list li { margin-bottom: 0.6em; font-size: 11pt; line-height: 1.6; }' +
    '.toc-list .ch-num { display: inline-block; width: 4em; font-weight: bold; color: #444; }' +
    '.toc-list .ch-title { color: #222; }' +
    '.img-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5em; margin: 1em 0; }' +
    '.img-grid figure { margin: 0; }' +
    '.img-grid img { max-width: 100%; max-height: 4.5cm; object-fit: contain; }' +
    '.appendix { page-break-before: always; }' +
    '.appendix h2 { font-size: 18pt; margin-bottom: 1em; text-align: center; }' +
    '.appendix p { text-indent: 0; }'
)
def find_browser():
    for p in [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe', os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe'), r'C:\Program Files\Google\Chrome\Application\chrome.exe']:
        if Path(p).exists(): return p
    return None

def render_html(progress, orient='portrait', size='B5'):
    css = STYLE_CSS + PAGE_CSS.replace('__SIZE__', size).replace('__ORIENT__', orient) + BODY_CSS
    L = []
    L.append('<!DOCTYPE html>')
    L.append('<html lang="zh-CN">')
    L.append('<head>')
    L.append('<meta charset="utf-8">')
    L.append('<title>一千种方法赚到一千美元</title>')
    L.append('<style>' + css + '</style>')
    L.append('</head>')
    L.append('<body>')
    L.append('<div class="cover-page"><img src="' + str(COVER) + '" alt=""></div>')
    L.append('<div class="title-page">')
    L.append('<h1 class="chapter-title" style="page-break-before:avoid;font-size:30pt;">一千种方法赚到一千美元</h1>')
    L.append('<p class="center" style="font-size:13pt;color:#555;">——基于实际经验的实用建议，关于自主创业及利用闲暇时间赚钱</p>')
    L.append('<p class="center" style="margin-top:1.5em;font-size:14pt;">F. C. 米纳克 编</p>')
    L.append('<p class="translator-note">本中文译本基于 1940 年第三修订版<br>由本地大语言模型（Qwen3-8B）辅助翻译<br>2026 年</p>')
    L.append('</div>')
    L.append('<div class="toc-page">')
    L.append('<h2>目 录</h2>')
    L.append('<ul class="toc-list">')
    L.append('<li><span class="ch-num">一</span><span class="ch-title">扉页与版权 / Publisher Note / Contents</span></li>')
    L.append('<li><span class="ch-num">二</span><span class="ch-title">机遇敲门（OPPORTUNITY KNOCKS）—— John Cameron Aspley 著</span></li>')
    L.append('<li><span class="ch-num">三</span><span class="ch-title">查理·达格玛的雪茄盒销售</span></li>')
    L.append('<li><span class="ch-num">四</span><span class="ch-title">E. L. 科德：借福特起步的传奇</span></li>')
    L.append('<li><span class="ch-num">五</span><span class="ch-title">养殖兔子取毛</span></li>')
    L.append('<li><span class="ch-num">六</span><span class="ch-title">J. W. 罗伯茨父子雪茄邮购</span></li>')
    L.append('<li><span class="ch-num">七</span><span class="ch-title">切斯特·瑞安的掘金机</span></li>')
    L.append('<li><span class="ch-num">八</span><span class="ch-title">哈里·拉森与称重机生意</span></li>')
    L.append('<li><span class="ch-num">九</span><span class="ch-title">亚伦·鲁比诺：19岁摄影记者的创业路（含 130 张原书摄影作品）</span></li>')
    L.append('</ul></div>')
    s1 = progress['01_part0000_split_000']['items']
    L.append('<h1 class="chapter-title">一、扉页与版权</h1>')
    for i in range(4):
        it = s1[i]
        for para in [p.strip() for p in it['translation'].split(chr(10)) if p.strip()]:
            L.append('<p>' + html.escape(para) + '</p>')
    L.append('<h2 class="section">目录 (Contents)</h2>')
    for i in range(4, 24):
        it = s1[i]
        for para in [p.strip() for p in it['translation'].split(chr(10)) if p.strip()]:
            L.append('<p>' + html.escape(para) + '</p>')
    L.append('<h1 class="chapter-title">二、机遇敲门</h1>')
    L.append('<p class="center" style="color:#666;font-size:10pt;">（John Cameron Aspley 著）</p>')
    for i in range(24, len(s1) - 1):
        it = s1[i]
        for para in [p.strip() for p in it['translation'].split(chr(10)) if p.strip()]:
            L.append('<p>' + html.escape(para) + '</p>')
    ch_meta = [
        ('02_part0000_split_001', '三、查理·达格玛的雪茄盒销售'),
        ('03_part0000_split_002', '四、E. L. 科德：借福特起步的传奇'),
        ('04_part0000_split_003', '五、养殖兔子取毛'),
        ('05_part0000_split_004', '六、J. W. 罗伯茨父子雪茄邮购'),
        ('06_part0000_split_005', '七、切斯特·瑞安的掘金机'),
        ('07_part0000_split_006', '八、哈里·拉森与称重机生意'),
        ('08_part0000_split_007', '九、亚伦·鲁比诺：19岁摄影记者的创业路'),
    ]
    for ck, title in ch_meta:
        L.append('<h1 class="chapter-title">' + title + '</h1>')
        items = progress[ck]['items']
        for it in items:
            for para in [p.strip() for p in it['translation'].split(chr(10)) if p.strip()]:
                L.append('<p>' + html.escape(para) + '</p>')
            if it.get('images') and ck == '08_part0000_split_007':
                L.append('<h2 class="section" style="page-break-before:always;">亚伦·鲁比诺摄影作品（原书插图）</h2>')
                L.append('<div class="img-grid">')
                for src, alt in it['images']:
                    L.append('<figure><img src="' + src + '" alt=""></figure>')
                L.append('</div>')
    L.append('</body></html>')
    return chr(10).join(L)

def html_to_pdf(html_path, pdf_path):
    browser = find_browser()
    if not browser: raise RuntimeError('No Edge/Chrome')
    print('browser:', browser)
    subprocess.run([browser, '--headless=new', '--disable-gpu', '--no-sandbox', '--print-to-pdf=' + str(pdf_path), '--no-pdf-header-footer', '--virtual-time-budget=30000', str(html_path)], check=True, timeout=300)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--orientation', default='portrait', choices=['portrait', 'landscape'])
    ap.add_argument('--size', default='B5', choices=['A4', 'B5', 'A5'])
    ap.add_argument('--html-only', action='store_true')
    a = ap.parse_args()
    if not PROG.exists(): print('No progress.json'); return
    progress = json.loads(PROG.read_text(encoding='utf-8'))
    print('chapters:', len(progress))
    if not COVER.exists(): print('No cover.jpg'); return
    html_content = render_html(progress, a.orientation, a.size)
    HTML.write_text(html_content, encoding='utf-8')
    print('HTML:', HTML, len(html_content), 'bytes')
    if a.html_only: return
    html_to_pdf(HTML, PDF)
    print('PDF:', PDF, PDF.stat().st_size, 'bytes')

if __name__ == '__main__':
    main()