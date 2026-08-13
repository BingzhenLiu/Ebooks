# -*- coding: utf-8 -*-
# translate.py - 英中翻译 EPUB (Qwen3-8B + Ollama, 128K ctx, think=False)
import sys, io, json, time, re, argparse, os, urllib.request, urllib.error
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup

if sys.stdout.encoding and sys.stdout.encoding.lower().startswith("gbk"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = sys.stdout

EPUB_PATH = r"D:\personalprofile\电子书\大雁塔\One Thousand Ways to Make 1000 (F.C. Minaker) (z-library.sk, 1lib.sk, z-lib.sk).epub"
OUTPUT_DIR = Path(r"D:\personalprofile\电子书\大雁塔\translate_epub\output")
CHAPTERS_DIR = OUTPUT_DIR / "chapters"
IMAGES_DIR = OUTPUT_DIR / "images"
PROGRESS_FILE = OUTPUT_DIR / "progress.json"
OLLAMA_BASE = "http://127.0.0.1:11434"
MODEL_NAME = "modelscope.cn/Qwen/Qwen3-8B-GGUF:latest"
NUM_CTX = 131072
TEMPERATURE = 0.3
SYS = "你是英中翻译，专译 1930-1940 美国商业自助书。要求：1.直译为主；2.专名首次加注中文；3.商业术语用现代汉语；4.必要时加[译者注]；5.直接输出，不要思考或前言。仅输出译文。"

def strip_think(text):
    return re.sub("<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def translate_one(text, retries=3):
    if not text or not text.strip(): return text
    payload = json.dumps({"model": MODEL_NAME, "messages": [{"role":"system","content":SYS},{"role":"user","content":text}], "think": False, "stream": False, "options": {"num_ctx": NUM_CTX, "temperature": TEMPERATURE}}).encode("utf-8")
    url = OLLAMA_BASE + "/api/chat"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read())
                content = result.get("message", {}).get("content", "")
                if content: return content
        except urllib.error.URLError as e:
            print("  [retry {}/{}] URLError: {}".format(attempt+1, retries, e))
            time.sleep(3 * (attempt + 1))
        except Exception as e:
            print("  [retry {}/{}] {}: {}".format(attempt+1, retries, type(e).__name__, e))
            time.sleep(3 * (attempt + 1))
    return "[翻译失败] " + text[:200]

def parse_chapter(item):
    soup = BeautifulSoup(item.get_content(), "html.parser")
    title = ""
    for h in soup.find_all(["h1","h2","h3"]):
        h_t = h.get_text(strip=True)
        if h_t and len(h_t) < 200:
            title = h_t
            break
    raw = []
    for x in soup.find_all("p"):
        text = x.get_text(" ", strip=True)
        if not text: continue
        imgs = []
        for img in x.find_all("img"):
            src = img.get("src") or img.get("epub:src") or ""
            alt = img.get("alt") or ""
            if src: imgs.append((src, alt))
        raw.append((text, imgs))
    end_chars = chr(46)+chr(33)+chr(63)+chr(59)+chr(58)+chr(34)+chr(41)+chr(93)+chr(12290)+chr(65281)+chr(65311)+chr(65306)+chr(12301)+chr(12299)
    paragraphs = []
    buf_t = ""
    buf_i = []
    for text, imgs in raw:
        if not buf_t: buf_t = text; buf_i = list(imgs); continue
        last = buf_t.rstrip()[-1] if buf_t.rstrip() else ""
        if last in end_chars:
            paragraphs.append((buf_t, buf_i))
            buf_t = text; buf_i = list(imgs)
        else:
            buf_t = buf_t + " " + text
            buf_i.extend(imgs)
    if buf_t: paragraphs.append((buf_t, buf_i))
    return title, paragraphs

def render_bilingual_md(title, items, img_start=1):
    lines = ["# " + title, ""]
    idx = img_start
    for it in items:
        imgs = it.get("images") or []
        for src, alt in imgs:
            lines.append("![" + "图片 %02d: %s" % idx + "](" + "images/" + Path(src).name + ")")
            lines.append("<!-- 原 EPUB: src=%s, alt=%r -->" % (src, alt))
            lines.append("")
            idx += 1
        lines.append("> **原文**: " + it["original"])
        lines.append("")
        lines.append("> **译文**: " + it["translation"])
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("### 校对状态: 待校对")
    lines.append("")
    return chr(10).join(lines)

def save_progress(prog):
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    import tempfile, shutil
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.json', dir=str(PROGRESS_FILE.parent))
    try:
        with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
            f.write(json.dumps(prog, ensure_ascii=False, indent=2))
        for _ in range(5):
            try:
                shutil.move(tmp_path, str(PROGRESS_FILE))
                break
            except OSError:
                time.sleep(0.2)
        else:
            raise
    except:
        if os.path.exists(tmp_path): os.remove(tmp_path)
        raise

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spine_index", type=int, nargs="?", default=1)
    ap.add_argument("max_paragraphs", type=int, nargs="?", default=None)
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--show-only", action="store_true")
    a = ap.parse_args()
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    book = epub.read_epub(EPUB_PATH)
    if a.spine_index >= len(book.spine): print("ERROR OOR"); sys.exit(1)
    sid, _ = book.spine[a.spine_index]
    item = book.get_item_with_id(sid)
    if not item: print("ERROR no item"); sys.exit(1)
    cid = "%02d_%s" % (a.spine_index, Path(item.get_name()).stem)
    title, paragraphs = parse_chapter(item)
    print("[%02d] %s title=%r paragraphs=%d" % (a.spine_index, item.get_name(), title, len(paragraphs)))
    if a.max_paragraphs: paragraphs = paragraphs[:a.max_paragraphs]; print("  limit=%d" % a.max_paragraphs)
    prog = json.loads(PROGRESS_FILE.read_text(encoding="utf-8")) if PROGRESS_FILE.exists() else {}
    if a.reset and cid in prog: del prog[cid]; save_progress(prog); print("  reset")
    ch = prog.get(cid, {"items":[], "done":False, "title":title})
    items = ch.get("items", [])
    if a.show_only:
        if not items: print("  empty"); return
        md = render_bilingual_md(title or item.get_name(), items)
        with open(str(CHAPTERS_DIR / (cid + ".md")), "w", encoding="utf-8") as f:
            f.write(md)
        print("  rendered"); return
    if ch.get("done"): print("  done (use --reset)"); return
    t0 = time.time()
    for i, (pt, imgs) in enumerate(paragraphs):
        if i < len(items): print("  [%02d/%d] cached" % (i+1, len(paragraphs))); continue
        print("  [%02d/%d] translating: %r" % (i+1, len(paragraphs), pt[:50]))
        ts = time.time()
        tr = translate_one(pt)
        dt = time.time() - ts
        items.append({"original": pt, "translation": tr, "images": imgs})
        prog[cid] = {"items": items, "done": False, "title": title}
        save_progress(prog)
        print("             [%.1fs]" % dt)
    print("total: %.1fs" % (time.time()-t0))
    md = render_bilingual_md(title or item.get_name(), items)
    with open(str(CHAPTERS_DIR / (cid + ".md")), "w", encoding="utf-8") as f:
        f.write(md)
    prog[cid]["done"] = True
    save_progress(prog)
    print("done!")

if __name__ == "__main__":
    main()