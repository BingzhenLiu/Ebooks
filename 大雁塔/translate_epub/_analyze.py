import json;prog=json.loads(open(r'D:\personalprofile\电子书\大雁塔\translate_epub\output\progress.json',encoding='utf-8').read());items=prog['01_part0000_split_000']['items']
for i,it in enumerate(items):
    t=it['translation']
    if '你现在可能会说' in t or 'NEVER in the history' in it['original']:
        print(f'OPPORTUNITY KNOCKS starts at item[{i}]')
        print('  orig:',it['original'][:100])
        print('  tr  :',t[:100])
        break
