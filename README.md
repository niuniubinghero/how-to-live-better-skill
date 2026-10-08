# how-to-live-better-skill · AI 技能版

把开源书《高性价比人生指南》的全部 **34 节 672 条**做成一个 AI Agent 技能：正文全部内置、**离线可检索**，装上以后直接问「替朋友担保签不签」「被裁了先做什么」「通勤两小时值不值」，Agent 会先把书里的相关条目查出来，再照书里的算账方式回答，并注明出自第几节第几条。

原书：<https://github.com/eternity4719/HowToLiveBetter>（正文 CC BY 4.0，作者 eternity4719）
本仓库只做三件事：把正文搬进来、做成可检索的索引、写成符合 [Agent Skills 开放标准](https://agentskills.io/specification)（agentskills.io）的技能包。**不改动原书任何一个字。**

## 和原书自带的 skill 有什么不同

原书仓库里也带了一个 skill，但它是「纯指令型」的：每次都要你先 `git clone` 现取正文，检索靠手写 `grep`。本仓库是「自带全文 + 脚本检索」——克隆下来就能用，不联网、不依赖原书网络可达。

## 目录结构

```
.
├── SKILL.md                 技能主文件（Agent 读它决定怎么用）
├── scripts/
│   ├── search.py            检索入口：关键词 + 多维筛选
│   ├── build_index.py       从 references/book/ 重建 data/items.json
│   ├── sync_upstream.py     追上游更新（支持 --dry-run）
│   └── install.py           装到各家 Agent 的技能目录 / 规范自检 / 打分发包
├── references/
│   ├── book/                原书正文 34 节全文（离线来源）
│   ├── 原书README.md        术语表、节-问题对照、作者写的「怎么读」
│   ├── 章节速览.md          34 节速览表
│   └── 极高性价比清单.md    114 条「极高」清单
└── data/items.json          672 条结构化索引（本地生成，不入库）
```

## 安装

格式是通用的，但**规范不规定放在哪个目录**，每家客户端自己挑。最简单的办法：

```bash
python scripts/install.py            # 装到 ~/.agents/skills/ + ~/.claude/skills/（覆盖几乎所有客户端）
python scripts/install.py --all      # 所有识别到的位置都装一份
python scripts/install.py --list     # 看本机各家目录装没装
python scripts/install.py --check    # 只做规范自检
python scripts/install.py --project <仓库>   # 装成项目级，随 git 共享给同事
```

也可以手动复制整个目录。各家的默认位置：

| Agent | 用户级 | 项目级 |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex / ChatGPT | `~/.codex/skills/` 或 `~/.agents/skills/` | `.agents/skills/` |
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| GitHub Copilot / VS Code | `~/.copilot/skills/` | `.github/skills/` |
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` |
| Windsurf | `~/.windsurf/skills/` | `.agents/skills/` |
| OpenCode / Goose | `~/.config/opencode/skills/` · `~/.config/goose/skills/` | — |
| WorkBuddy | `~/.workbuddy/skills/` | `.workbuddy/skills/` |

`~/.agents/skills/` 是跨客户端公约路径，除 Claude Code 外各家都读它。

## 用法

**首次使用先生成索引**（仓库不带索引，约 2.9 MB，由正文随时重建）：

```bash
python scripts/build_index.py      # 生成 data/items.json 和两份速查，约 2 秒
```

装上以后直接问就行。要手动查：

```bash
python scripts/search.py "担保 签不签"                # 关键词检索
python scripts/search.py "被裁 补偿" -k 12 --grade A  # 只要 A 级证据
python scripts/search.py "降压" --ratio 极高          # 只要极高性价比
python scripts/search.py "押金" --sec 15 --full       # 限定节 + 打印条目全文
python scripts/search.py --item 8.18                  # 按「节.条」定位
python scripts/search.py --sec 13 --all               # 整节速览
```

筛选：`--grade A|B|C`、`--ratio 极高|高|一般`、`--sec`、`--kj 金钱|死亡率|时间|自由`、`--free`（不花钱）、`--easy`（不需毅力）、`--dispute`（只看标了争议的）。

脚本纯 Python 标准库，无第三方依赖。

## 数据口径

| 项 | 数量 |
| --- | --- |
| 条目 | 672 |
| 证据等级 | A 438 / B 179 / C 55 |
| 性价比 | 极高 114 / 高 304 / 一般 254 |
| 标注争议 | 70 |

性价比档位的算法（成本分 = 钱 + 时间 + 毅力三项权重，再配收益量级）固化在 `scripts/build_index.py` 的 `ratio_of()`，抄自原书 `tools/lib/book.mjs`，与线上检索页一致。**换过 `references/book/` 之后必须重跑 `python scripts/build_index.py`**，否则检索用的是旧索引。

追上游更新：`python scripts/sync_upstream.py --dry-run` 先看差异，确认后去掉参数执行。

## 许可与署名

- 正文 `references/book/` 与原书 README 来自 eternity4719/HowToLiveBetter，许可 **CC BY 4.0**，完整条款见 [LICENSE](LICENSE)。
- 本仓库的脚本与整理稿沿用同一许可。
- 引用时请保留原书出处与「第 X 节第 Y 条」的定位。

## 说明

这本书给的是通用口径，不替代医生、律师、会计。法律与社保内容按中国大陆现行规定写，制度会变，涉及金额、期限、程序时以当时的官方文件为准。本项目从未发行也不会发行任何代币。
