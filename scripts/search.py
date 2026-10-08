# -*- coding: utf-8 -*-
"""《高性价比人生指南》条目检索。

    python scripts/search.py "担保 签不签"                 # 关键词检索（默认 8 条）
    python scripts/search.py "裁员 补偿" -k 12 --grade A    # 只要 A 级证据
    python scripts/search.py "降压" --ratio 极高            # 只要极高性价比
    python scripts/search.py "押金" --sec 15 --full         # 限定第 15 节并打印条目全文
    python scripts/search.py --item 8.17                    # 按「节.条」直接定位，打印全文
    python scripts/search.py --sec 13 --all                 # 整节速览（标题 + 说人话）

筛选：--grade A|B|C  --ratio 极高|高|一般  --sec 8,13  --口径 金钱|死亡率|时间|自由
      --free（不花钱）  --easy（不需要毅力）  --dispute（只看标了争议的）
输出：--full（打印命中条目的完整原文）  -k N（条数，默认 8）
纯标准库，无第三方依赖，不联网。
"""
import os, re, io, sys, json, argparse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(BASE, 'data', 'items.json')
BOOK = os.path.join(BASE, 'references', 'book')

_LEVEL_ORDER = {'A': 0, 'B': 1, 'C': 2}
_RATIO_ORDER = {'极高': 0, '高': 1, '一般': 2}


def load():
    if not os.path.exists(IDX):
        sys.exit('索引不存在，先跑：python scripts/build_index.py')
    return json.load(io.open(IDX, encoding='utf-8'))


def score(item, tokens):
    """命中打分，返回 (分数, 是否整词命中)。

    整词子串命中为主，标题再加权；整词都没命中才退到字符二元组（模糊档，权重低）。
    """
    hay = item['haystack']
    s = 0.0
    for t in tokens:
        c = hay.count(t)
        if c:
            s += c * (len(t) ** 1.5)
            if t in item['title']:
                s += 6 * len(t)
    if s > 0:
        return s, True
    q = ''.join(tokens)
    grams = {q[i:i + 2] for i in range(len(q) - 1)}
    for g in grams:
        s += hay.count(g) * 0.6
    return s, False


def full_text(sec, no):
    """从 references/book/ 里抽出整条原文。"""
    hits = [p for p in os.listdir(BOOK) if p.startswith(f'{sec:02d}-') or p.startswith(f'{sec}-')]
    if not hits:
        return '(找不到第 %d 节正文)' % sec
    path = os.path.join(BOOK, sorted(hits)[0])
    lines = io.open(path, encoding='utf-8').read().split('\n')
    start = None
    for i, ln in enumerate(lines):
        if re.match(r'^### %d\.\s' % no, ln):
            start = i
            break
    if start is None:
        return '(第 %d 节里没有第 %d 条)' % (sec, no)
    out = []
    for ln in lines[start:]:
        if out and re.match(r'^### \d+\.\s', ln):
            break
        if ln.startswith('[← 回总目录]'):
            break
        out.append(ln)
    return '\n'.join(out).rstrip()


def brief(it, width=200):
    return '[%d.%d] %s' % (it['sec'], it['no'], it['title'])


def show(it, full=False):
    width = 200
    tag = it.get('tag', {})
    flags = ' '.join(f'{k}={tag[k]}' for k in ('钱', '时间', '毅力', '收益') if k in tag)
    marks = ('⚠争议' if it['dispute'] else '') + (' ⚑待核实' if it['todo'] else '')
    print('[%d.%d] %s  `%s`  性价比:%s  成本:%s  口径:%s%s'
          % (it['sec'], it['no'], it['title'], it['level'], it['ratio'], flags, tag.get('口径', ''),
             ('  ' + marks) if marks else ''))
    plain = it['plain']
    print('    说人话：' + (plain if len(plain) <= width else plain[:width] + '…'))
    if full:
        print('\n' + full_text(it['sec'], it['no']) + '\n')


def main():
    ap = argparse.ArgumentParser(add_help=True, description='《高性价比人生指南》条目检索')
    ap.add_argument('query', nargs='*', help='关键词，空格分隔')
    ap.add_argument('-k', type=int, default=8, help='返回条数，默认 8')
    ap.add_argument('--grade', help='证据等级过滤，如 A 或 A,B')
    ap.add_argument('--ratio', help='性价比过滤，如 极高 或 极高,高')
    ap.add_argument('--sec', help='限定节号，如 8 或 8,13')
    ap.add_argument('--kj', dest='kj', help='口径过滤：金钱/死亡率/时间/自由')
    ap.add_argument('--free', action='store_true', help='只要不花钱的（钱=0）')
    ap.add_argument('--easy', action='store_true', help='只要不需要毅力的（毅力=否）')
    ap.add_argument('--dispute', action='store_true', help='只要标了争议的条目')
    ap.add_argument('--full', action='store_true', help='打印命中条目完整原文')
    ap.add_argument('--item', help='按「节.条」直接定位，如 8.17，逗号分隔多条')
    ap.add_argument('--all', action='store_true', help='与 --sec 同用，整节速览，不做打分')
    a = ap.parse_args()

    data = load()
    items = data['items']

    # 直接定位
    if a.item:
        for ref in a.item.split(','):
            m = re.match(r'^(\d+)\.(\d+)$', ref.strip())
            if not m:
                print('条目号要写成「节.条」，例如 8.17')
                continue
            sec, no = int(m.group(1)), int(m.group(2))
            hit = next((i for i in items if i['sec'] == sec and i['no'] == no), None)
            if not hit:
                print(f'没有第 {sec}.{no} 条')
                continue
            print(f'\n===== 第 {sec}.{no} 条 =====\n')
            print(full_text(sec, no))
        return

    # 过滤
    pool = items
    if a.grade:
        gs = [x.strip() for x in a.grade.split(',')]
        pool = [i for i in pool if i['level'] in gs]
    if a.ratio:
        rs = [x.strip() for x in a.ratio.split(',')]
        pool = [i for i in pool if i['ratio'] in rs]
    if a.sec:
        ss = [int(x) for x in re.split(r'[,\s]+', a.sec.strip()) if x]
        pool = [i for i in pool if i['sec'] in ss]
    if a.kj:
        pool = [i for i in pool if i.get('tag', {}).get('口径') == a.kj]
    if a.free:
        pool = [i for i in pool if i.get('tag', {}).get('钱') == '0']
    if a.easy:
        pool = [i for i in pool if i.get('tag', {}).get('毅力') == '否']
    if a.dispute:
        pool = [i for i in pool if i['dispute']]

    if a.sec and a.all and not a.query:
        print(f'# 第 {a.sec} 节共 {len(pool)} 条\n')
        for it in sorted(pool, key=lambda x: x['no']):
            show(it)
        return

    if not a.query:
        ap.print_help()
        return

    tokens = [t for t in re.split(r'[\s,，、;；/|]+', ' '.join(a.query)) if t]
    raw = [(score(i, tokens), i) for i in pool]
    exact, fuzzy = [], []
    for (s, ok), i in raw:
        if s <= 0:
            continue
        (exact if ok else fuzzy).append((s, i))
    exact.sort(key=lambda x: (-x[0], _RATIO_ORDER[x[1]['ratio']],
                              _LEVEL_ORDER[x[1]['level']], x[1]['sec'], x[1]['no']))
    fuzzy.sort(key=lambda x: (-x[0], _RATIO_ORDER[x[1]['ratio']],
                              _LEVEL_ORDER[x[1]['level']], x[1]['sec'], x[1]['no']))
    # 有精确命中时，压掉只靠一两个字碰上的模糊结果（阈值 1.2 = 至少两个二元组命中）
    if exact:
        fuzzy = [x for x in fuzzy if x[0] >= 1.2]
    scored = exact + fuzzy
    if not scored:
        print('没有命中。换更短的词再试，或去掉筛选条件；也可以直接 grep 正文：')
        print('  grep -rn "关键词" references/book/')
        return
    print(f'# 命中 {len(scored)} 条，显示前 {min(a.k, len(scored))} 条\n')
    for _, it in scored[:a.k]:
        show(it, full=a.full)


if __name__ == '__main__':
    main()
