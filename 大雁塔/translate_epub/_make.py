import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path
L = []
Q = chr(39); DQ = chr(34); NL = chr(10)
def A(s): L.append(s)
A('# -*- coding: utf-8 -*-')
A('# build_pdf.py - 双语对照 PDF 生成器 (HTML + Edge headless)')
A('# 用法: python build_pdf.py [--orientation landscape|portrait] [--size A4|B5|A5] [--chapter N]')
A('import sys, io, json, html, subprocess, os, argparse')
A('from pathlib import Path')
A('if sys.stdout.encoding and sys.stdout.encoding.lower().startswith(' + DQ + 'gbk' + DQ + '):')
A('    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=' + DQ + 'utf-8' + DQ + ', errors=' + DQ + 'replace' + DQ + ')')
A('    sys.stderr = sys.stdout')
A('OUTPUT_DIR = Path(r' + DQ + 'D:' + DQ + ' + chr(92)*2 + 'personalprofile' + chr(92)*2 + 'ebook' + chr(92)*2 + 'dayanta' + chr(92)*2 + 'translate_epub' + chr(92)*2 + 'output' + DQ + ')')