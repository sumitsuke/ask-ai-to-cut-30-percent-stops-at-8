# -*- coding: utf-8 -*-
"""T34 採点: outputs/main/*.md を atoms_claims_frozen.json に当てる。
   列＝変化率／atom の残存（multiset: 原文の出現回数 vs 出力の出現回数・落ちた個数）／claim の残存（正規化文字列の一致＝自動 PASS、不一致＝人の裁定へ）／構造（見出し数・箇条書き数）
   出力: score.csv（1 行＝1 出力）・claims_to_judge.csv（不一致の claim を人が「言い換えて残った／落ちた／反転」で裁定する表）・summary.md"""
import io, os, re, json, csv, glob, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
F = json.load(io.open(os.path.join(HERE, 'atoms_claims_frozen.json'), encoding='utf-8'))['articles']
ATOM = re.compile(r'([\d,]+(?:\.\d+)?)\s*(円|件|本|日|時間|営業日|%|％|項目|段階|か所|回|人|社|通|枚|行|字|ミリ秒|秒|分|か月|つ|層|型|種|点|倍)')
def plain(s): return re.sub(r'<[^>]+>', '', s)
def tlen(s): return len(re.sub(r'\s', '', plain(s)))
def norm(s): return re.sub(r'[\s*_`「」（）()\[\]【】、。・:：―—-]', '', plain(s))
def atoms_of(s):
    d = {}
    for m in ATOM.finditer(plain(s)): k = f'{m.group(1)} {m.group(2)}'; d[k] = d.get(k, 0) + 1
    return d
def structure(s): return (len(re.findall(r'^#{1,6} ', s, re.M)), len(re.findall(r'^\s*(?:[-*]|\d+\.) ', s, re.M)))
rows = []; judge = []
for f in sorted(glob.glob(os.path.join(HERE, 'outputs', 'main', '*.md'))):
    slug, cond, rep = os.path.basename(f)[:-3].split('__')
    src = io.open(os.path.join(HERE, 'materials', slug + '.md'), encoding='utf-8').read()
    out = io.open(f, encoding='utf-8').read()
    a0, a1 = F[slug]['atoms'], atoms_of(out)
    lost = {k: c - a1.get(k, 0) for k, c in a0.items() if a1.get(k, 0) < c}
    n_out = norm(out); hit = 0
    for c in F[slug]['claims']:
        if norm(c) in n_out: hit += 1
        else: judge.append([slug, cond, c, '', ''])
    s0, s1 = structure(src), structure(out)
    rows.append({'slug': slug, 'cond': cond, 'src_chars': tlen(src), 'out_chars': tlen(out), 'change_pct': round((tlen(out) - tlen(src)) / tlen(src) * 100, 1), 'reached_-20': tlen(out) <= tlen(src) * 0.8, 'atoms_total': sum(a0.values()), 'atoms_lost': sum(lost.values()), 'atoms_lost_list': ';'.join(f'{k}×{v}' for k, v in lost.items()), 'claims_total': len(F[slug]['claims']), 'claims_auto_pass': hit, 'claims_to_judge': len(F[slug]['claims']) - hit, 'headings_src_out': f'{s0[0]}/{s1[0]}', 'bullets_src_out': f'{s0[1]}/{s1[1]}'})
with io.open(os.path.join(HERE, 'score.csv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# 09-19 夜: A〜C の 33 行は裁定済（claims_judged_2026-09-19.csv）。条件 0 の不一致だけを別表に出す（人の裁定へ）
with io.open(os.path.join(HERE, 'claims_to_judge_cond0.csv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh); w.writerow(['slug', 'cond', 'claim', '裁定（言い換えて残った／落ちた／反転）', '根拠']); w.writerows([j for j in judge if j[1] == '0'])
lines = ['| 条件 | n | 変化率 中央値 | 四分位 | 最小／最大 | −20% に届いた | atom 落ち（合計／本数） | claim 自動 PASS | 人の裁定へ |', '|---|---|---|---|---|---|---|---|---|']
for cond in '0ABC':
    rs = [r for r in rows if r['cond'] == cond]; ch = sorted(r['change_pct'] for r in rs); n = len(ch)
    lines.append(f"| {cond} | {n} | {st.median(ch):.1f}% | {ch[n//4]:.1f}〜{ch[(3*n)//4]:.1f} | {ch[0]:.1f}／{ch[-1]:.1f} | {sum(r['reached_-20'] for r in rs)} | {sum(r['atoms_lost'] for r in rs)}／{sum(1 for r in rs if r['atoms_lost'])} | {sum(r['claims_auto_pass'] for r in rs)}／{sum(r['claims_total'] for r in rs)} | {sum(r['claims_to_judge'] for r in rs)} |")
io.open(os.path.join(HERE, 'summary.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines)); print('judge rows', len(judge))
