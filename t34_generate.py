# -*- coding: utf-8 -*-
"""T34 生成: claude -p（清潔な cwd＝TEMP/t34・CLAUDE.md なし）で 1 本 1 呼び出し。指示 3 条件（入れ子・逐語）。
python t34_generate.py pilot   → 3 本 × 条件 A × 3 回（再現の幅）
python t34_generate.py main    → 14 本 × 3 条件（記事ごとに条件の順をランダム化・乱数種 20260919）
python t34_generate.py cond0   → 14 本 × 条件 0（制約なし＝「20〜30% 短く」だけ・09-19 夜の裁定 🙋3 で追加。A〜C の「構造を変えない」の効果を分離する対照）
出力: outputs/<mode>/<slug>__<cond>__<rep>.md と log.csv（時刻・所要秒・字数）"""

import io, os, sys, subprocess, time, random, re, json, csv

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(HERE, "materials")
MODEL = "claude-opus-5"
COND = {
    "0": "次の本文を 20〜30% 短くしてください。短くした本文だけを出力してください（前置きや説明は不要）。",
    "A": "次の本文を 20〜30% 短くしてください。見出し・段落・箇条書きの構造は変えないでください。短くした本文だけを出力してください（前置きや説明は不要）。",
    "B": "次の本文を 20〜30% 短くしてください。見出し・段落・箇条書きの構造は変えないでください。数字と、条件・限界・例外を述べた文は残してください。短くした本文だけを出力してください（前置きや説明は不要）。",
    "C": "次の本文を 20〜30% 短くしてください。見出し・段落・箇条書きの構造は変えないでください。数字と、条件・限界・例外を述べた文は残してください。ただし列挙は箇条書きに変えて構いません。短くした本文だけを出力してください（前置きや説明は不要）。",
}
CWD = os.path.join(os.environ["TEMP"], "t34")
os.makedirs(CWD, exist_ok=True)


def text_only(s):
    return len(re.sub(r"\s", "", re.sub(r"<[^>]+>", "", s)))


def gen(slug, cond, rep, mode):
    body = io.open(os.path.join(M, slug + ".md"), encoding="utf-8").read()
    prompt = COND[cond] + "\n\n---\n\n" + body
    out_dir = os.path.join(HERE, "outputs", mode)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{slug}__{cond}__{rep}.md")
    if os.path.exists(out):
        return
    t0 = time.time()
    # 長い日本語の本文を argv で渡すと Windows の shell 経由で落ちる（予備の初回＝本文が届かず「本文が含まれていない」）→ stdin で渡す
    r = subprocess.run(
        ["claude", "-p", "--model", MODEL],
        input=prompt,
        cwd=CWD,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=True,
        timeout=600,
    )
    txt = r.stdout.strip()
    io.open(out, "w", encoding="utf-8", newline="\n").write(txt + "\n")
    with io.open(os.path.join(HERE, "outputs", "log.csv"), "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(
            [
                mode,
                slug,
                cond,
                rep,
                time.strftime("%Y-%m-%dT%H:%M:%S"),
                round(time.time() - t0),
                text_only(body),
                text_only(txt),
                r.returncode,
                (r.stderr or "")[:120].replace("\n", " "),
            ]
        )
    print(mode, slug, cond, rep, f"{text_only(body)}→{text_only(txt)}", f"{round(time.time() - t0)}s", flush=True)


mode = sys.argv[1]
slugs = sorted(os.path.splitext(f)[0] for f in os.listdir(M) if f.endswith(".md"))
if mode == "cond0":
    for slug in slugs:
        gen(slug, "0", 1, "main")
elif mode == "pilot":
    for slug in slugs[:3]:
        for rep in (1, 2, 3):
            gen(slug, "A", rep, "pilot")
else:
    rnd = random.Random(20260919)
    order = {}
    for slug in slugs:
        conds = ["A", "B", "C"]
        rnd.shuffle(conds)
        order[slug] = conds
    io.open(os.path.join(HERE, "outputs", "main_order.json"), "w", encoding="utf-8").write(
        json.dumps({"seed": 20260919, "order": order}, ensure_ascii=False, indent=1)
    )
    for slug in slugs:
        for cond in order[slug]:
            gen(slug, cond, 1, "main")
print("done")
