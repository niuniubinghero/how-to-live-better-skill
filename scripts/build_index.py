# -*- coding: utf-8 -*-
"""从 references/book/*.md 重建索引。

产出：
  data/items.json                    672 条结构化索引（检索脚本读它）
  references/章节速览.md              34 节速览表（节名 / 回答什么问题 / 条数 / A·B·C / 极高条数）
  references/极高性价比清单.md        114 条「极高」清单（不花钱、不占时间、不需毅力、收益最大档）

用法：
  python scripts/build_index.py
纯标准库，无第三方依赖。
"""
import os, re, json, glob, io

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = os.path.join(BASE, 'references', 'book')
DATA = os.path.join(BASE, 'data')
README = os.path.join(BASE, 'references', '原书README.md')

# 成本标签三档权重与档位规则，抄自原书 tools/lib/book.mjs（与 index.html 的 COST_W / e.ratio 一致）
W = {'money': {'0': 0, '少': 1, '多': 2},
     'time': {'少': 0, '中': 1, '多': 2},
     'will': {'否': 0, '些': 1, '是': 2}}


def ratio_of(cost, level):
    if level == '大':
        return '极高' if cost == 0 else ('高' if cost <= 2 else '一般')
    return '高' if (level == '中' and cost == 0) else '一般'


def load_questions():
    """从原书 README 抽「本节回答什么问题」对照表。"""
    q = {}
    if not os.path.exists(README):
        return q
    txt = io.open(README, encoding='utf-8').read()
    for m in re.finditer(r'^\|\s*(.+?)\s*\|\s*\[(.+?)\]\(book/(\d+)-.+?\.md\)\s*\|$', txt, re.M):
        q[int(m.group(3))] = (re.sub(r'^\d+\.\s*', '', m.group(2)), m.group(1).strip('*').strip())
    return q


def parse():
    items = []
    sections = []
    files = sorted(glob.glob(os.path.join(BOOK, '*.md')))
    for f in files:
        m = re.match(r'(\d+)-(.+)\.md', os.path.basename(f))
        sec_no, sec_name = int(m.group(1)), m.group(2)
        cur = None
        n = 0
        for ln in io.open(f, encoding='utf-8').read().split('\n'):
            mt = re.match(r'^### (\d+)\.\s*(.+)$', ln)
            if mt:
                cur = {'sec': sec_no, 'sec_name': sec_name, 'no': int(mt.group(1)),
                       'title': mt.group(2).strip(), 'plain': '', 'cost': '', 'benefit': '',
                       'level': '', 'source': '', 'note': '', 'dispute': False, 'todo': False}
                items.append(cur)
                n += 1
                continue
            if cur is None:
                continue
            mt = re.match(r'^<!--\s*成本标签:\s*钱=(\S+)\s+时间=(\S+)\s+毅力=(\S+)\s+收益=(\S+)\s+口径=(\S+?)\s*-->', ln)
            if mt:
                cur['tag'] = {'钱': mt.group(1), '时间': mt.group(2), '毅力': mt.group(3),
                              '收益': mt.group(4), '口径': mt.group(5)}
                cost = W['money'][mt.group(1)] + W['time'][mt.group(2)] + W['will'][mt.group(3)]
                cur['ratio'] = ratio_of(cost, mt.group(4))
                continue
            for key, prefix in (('cost', '- 成本：'), ('plain', '- 说人话：'), ('benefit', '- 收益：'),
                                ('source', '- 来源：'), ('note', '- 备注：')):
                if ln.startswith(prefix):
                    cur[key] = ln[len(prefix):].strip()
                    break
            else:
                if ln.startswith('- 证据等级：'):
                    cur['level'] = ln[len('- 证据等级：'):].strip()[:1]
                    continue
            if cur['note'].startswith('争议'):
                cur['dispute'] = True
            if '待核实' in ln or 'TODO' in ln:
                cur['todo'] = True
        sections.append({'no': sec_no, 'name': sec_name, 'count': n})
    return items, sections


def main():
    items, sections = parse()
    os.makedirs(DATA, exist_ok=True)
    # 检索用的正文：标题 + 说人话 + 收益；备注和来源只留前 400 字，控制体积
    for it in items:
        # 检索正文把节名也带上：像「程序员」「出国」这类词写在节名里，不在条目标题里
        it['haystack'] = '\n'.join([f"第{it['sec']}节 {it['sec_name']}", it['title'],
                                    it['plain'], it['benefit'], it['note'][:300]])
    with io.open(os.path.join(DATA, 'items.json'), 'w', encoding='utf-8') as fp:
        json.dump({'generated_from': 'references/book/*.md', 'sections': sections, 'items': items},
                  fp, ensure_ascii=False)

    qmap = load_questions()
    stat = {}
    for it in items:
        s = stat.setdefault(it['sec'], {'n': 0, 'A': 0, 'B': 0, 'C': 0, '极高': 0, '高': 0, '一般': 0})
        s['n'] += 1
        s[it['level']] = s.get(it['level'], 0) + 1
        s[it['ratio']] = s.get(it['ratio'], 0) + 1

    out = ['# 34 节速览\n',
           '（「极高」= 该节内性价比极高的条数，是优先看的入口；A/B/C = 该节证据等级分布）\n',
           '| # | 章节 | 回答什么问题 | 条数 | A/B/C | 极高 |', '| --- | --- | --- | --- | --- | --- |']
    for no in sorted(stat):
        name, q = qmap.get(no, (sections[no - 1]['name'], ''))
        st = stat[no]
        out.append(f"| {no} | {name} | {q} | {st['n']} | {st['A']}/{st['B']}/{st['C']} | {st['极高']} |")
    out.append(f"| **合计** | | | **{len(items)}** | "
               f"**{sum(1 for i in items if i['level']=='A')}/{sum(1 for i in items if i['level']=='B')}/{sum(1 for i in items if i['level']=='C')}** | "
               f"**{sum(1 for i in items if i['ratio']=='极高')}** |")
    io.open(os.path.join(BASE, 'references', '章节速览.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')

    top = [i for i in items if i['ratio'] == '极高']
    o2 = ['# 114 条「极高性价比」清单\n',
          '口径：收益=大 且 钱=0、时间=少、毅力=否（不花钱、不额外占时间、不需要坚持）。\n',
          '每条附原书「说人话」原文；`A/B/C` 为证据等级，`⚠` 为原书标注争议。']
    for no in sorted(stat):
        grp = [i for i in top if i['sec'] == no]
        if not grp:
            continue
        name = qmap.get(no, (sections[no - 1]['name'], ''))[0]
        o2.append(f"\n## 第 {no} 节 · {name}（{len(grp)} 条）\n")
        for it in grp:
            o2.append(f"- **{no}.{it['no']} {it['title']}** `{it['level']}{'⚠' if it['dispute'] else ''}`\n"
                      f"  - 说人话：{it['plain']}")
    io.open(os.path.join(BASE, 'references', '极高性价比清单.md'), 'w', encoding='utf-8').write('\n'.join(o2) + '\n')

    print(f'条目 {len(items)} 条 / 节 {len(sections)} 节')
    print('证据等级 A/B/C:', sum(1 for i in items if i['level'] == 'A'),
          sum(1 for i in items if i['level'] == 'B'), sum(1 for i in items if i['level'] == 'C'))
    print('性价比 极高/高/一般:', sum(1 for i in items if i['ratio'] == '极高'),
          sum(1 for i in items if i['ratio'] == '高'), sum(1 for i in items if i['ratio'] == '一般'))


if __name__ == '__main__':
    main()
