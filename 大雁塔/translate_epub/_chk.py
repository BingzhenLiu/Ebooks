import sys,io;sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace');from ebooklib import epub;from bs4 import BeautifulSoup;book=epub.read_epub(r'D:\personalprofile\电子书\大雁塔\One Thousand Ways to Make 1000 (F.C. Minaker) (z-library.sk, 1lib.sk, z-lib.sk).epub');sp=list(book.spine);sid,_=sp[8];it=book.get_item_with_id(sid);soup=BeautifulSoup(it.get_content(),'html.parser')
# 看 body 所有直接子元素的类型分布
from collections import Counter
ctr=Counter()
for c in soup.body.children:
    if hasattr(c,'name'):
        ctr[c.name]+=1
print('body direct children:',dict(ctr))
# 找所有 <img> 的父级
imgs=soup.find_all('img')
print(f'total imgs: {len(imgs)}')
# 每个 img 的 parent 类型分布
parents=Counter(str(img.parent.name) for img in imgs)
print('img parents:',dict(parents))
# 第一个 img 的前一个 <p>
if imgs:
    first=imgs[0];prev_p=first.find_previous('p');print('first img prev p:',prev_p.get_text(' ',strip=True)[:80] if prev_p else None)
