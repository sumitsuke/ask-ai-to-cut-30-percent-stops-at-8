# -*- coding: utf-8 -*-
"""T34 工程 1: 材料 14 本を凍結し、protected atom（値＋単位＋主張・出現回数込み）と境界 claim の候補を出す。
   出力: materials/<slug>.md（本文＝frontmatter と末尾 CTA を除く・Markdown のまま）・atoms_claims_candidates.json・materials_sha256.txt
   境界 claim は正規表現で候補出し→ 人（当方）が通読して確定＝atoms_claims_frozen.json（除いた候補数を書く）"""
import sys, io, os, re, glob, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'materials')   # 元＝サイトの src/content/guide（09-19 夜: 絶対パスを引数に。materials/ が既にあればそれを読む）
M = os.path.join(HERE, 'materials'); os.makedirs(M, exist_ok=True)
ATOM = re.compile(r'([\d,]+(?:\.\d+)?)\s*(円|件|本|日|時間|営業日|%|％|項目|段階|か所|回|人|社|通|枚|行|字|ミリ秒|秒|分|か月|つ|層|型|種|点|倍)')
CLAIM = re.compile(r'[^。\n]*?(ない場合|限界|確かめていない|検証していない|測っていない|ただし|例外|保証|ではありません|とは限りません|できません|しません|だけです|まで(?:です|は|に))[^。\n]*。')
def text_only(s):
    s = re.sub(r'<[^>]+>', '', s); return re.sub(r'\s', '', s)
out = {}; sha = []
for f in sorted(glob.glob(os.path.join(SRC, '*.md'))):
    slug = os.path.splitext(os.path.basename(f))[0]
    raw = io.open(f, encoding='utf-8').read()
    body = raw.split('---', 2)[2]
    # 末尾の CTA・根拠・関連（「## 依頼の前に」以降や「- 実績:」「- この記事の根拠:」の行）は材料から外す＝本文だけ
    body = re.split(r'\n## (?:依頼の前に|根拠|関連)', body)[0].strip() + '\n'
    p = os.path.join(M, slug + '.md'); io.open(p, 'w', encoding='utf-8', newline='\n').write(body)
    h = hashlib.sha256(body.encode('utf-8')).hexdigest(); sha.append(f'{h}  {slug}.md')
    plain = re.sub(r'<[^>]+>', '', body)
    atoms = {}
    for m in ATOM.finditer(plain):
        val, unit = m.group(1), m.group(2)
        ctx = plain[max(0, m.start() - 12): m.end() + 8].replace('\n', ' ')
        key = f'{val} {unit}'; atoms.setdefault(key, []).append(ctx)
    claims = [c.strip() for c in CLAIM.findall(plain)] if False else [m.group(0).strip() for m in CLAIM.finditer(plain)]
    out[slug] = {'chars': len(text_only(body)), 'atoms': {k: {'count': len(v), 'contexts': v} for k, v in atoms.items()}, 'claim_candidates': claims}
    print(slug, out[slug]['chars'], 'atoms', sum(a['count'] for a in out[slug]['atoms'].values()), 'claims', len(claims))
io.open(os.path.join(HERE, 'atoms_claims_candidates.json'), 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
io.open(os.path.join(HERE, 'materials_sha256.txt'), 'w', encoding='utf-8').write('\n'.join(sha) + '\n')
