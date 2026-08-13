import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8",errors="replace")
from pathlib import Path
p=Path(r"D:\\personalprofile\\电子书\\大雁塔\\translate_epub\\translate.py")
t=p.read_text(encoding="utf-8")
o = chr(10).join([l for l in t.split(chr(10)) if "def translate_one" in l or "if not text or not text.strip()" in l or "for attempt in range" in l or (l.strip().startswith("try:") and "    " in l) or "client.chat.completions" in l or "resp.choices" in l or "return r" in l or "except Exception" in l or "time.sleep" in l or "return " in l and "失败" in l][:12])
print("OLD len:", len(o))
print(o[:100])
