---
name: how-to-live-better
description: 用《高性价比人生指南》（github.com/eternity4719/HowToLiveBetter，正文 CC BY 4.0，本地已内置 34 节 672 条全文）回答具体的人生决策：该不该做、值不值、怎么选、划不划算、出事了先做什么、能领哪笔钱、这么干犯不犯法、哪些钱别花。先检索出相关条目再回答，按成本（钱/时间/毅力）、收益量级、证据等级 A/B/C 排序，每条注明出自第几节第几条；查不到就直说查不到，不补数字。触发词：该不该、值不值、要不要、划不划算、怎么选、帮我决定、犯法吗、能领什么、先做什么、性价比、避坑、智商税、被裁、押金、担保、工伤。
license: CC BY 4.0（正文，来自 eternity4719/HowToLiveBetter）；脚本与整理稿同许可
compatibility: 纯离线可用。跑 scripts/search.py 需要 Python 3（仅标准库，无第三方依赖）；不跑脚本时全部内容可直接以 Markdown 阅读。
metadata:
  author: eternity4719（原书）/ 本地整理
  version: "1.0"
  upstream: https://github.com/eternity4719/HowToLiveBetter
  entries: "672"
agent_created: true
---

# 人生决策：查《高性价比人生指南》再答

## 这个技能做什么

有人问一件具体的人生事该怎么办，先从本地内置的正文中检索相关条目，再按书里的算账方式排好序回答。

**没查到就不答。** 答复里的每个数字、每条法条、每个结论都要能指回某一条正文；指不回去，就直说书里没写，可以给常识判断，但必须标明那是常识不是书里的内容。不要凭记忆补数字、补 DOI、补法条条款号。

书把要换回的东西分成四样：寿命、时间与精力、金钱、人身自由。**四样分开算，不互相折算**——「总死亡率降 12%」和「每年省 500 元」不在一把尺子上，不能排在一起比高下。

## 第 0 步：先看要不要马上停下

- **正在发生的急症**（倒地没呼吸、大出血、火灾、溺水、触电、中毒、卒中或心梗症状、从高处坠落）：先说打 120 / 119 和现场第一个动作，出处第 13 节，别先讲性价比。
- **提到自杀念头、活不下去**：先给全国心理援助热线 12356，再按第 1 节和第 29 节说，不做劝导式分析，不评价动机。
- **正在进行的法律程序**（已被传唤、已被拘留、已被起诉）：先指第 8 节对应条目，并说明书只给通用口径，个案要找律师。
- 其余情况照下面走。

## 第 1 步：检索

技能目录下已内置全部正文（`references/book/` 34 个文件）和结构化索引（`data/items.json` 672 条），**不联网、不克隆仓库**。

检索入口（`SKILL` 指本技能目录）：

```bash
python scripts/search.py "担保 签不签"              # 关键词，默认 8 条
python scripts/search.py "被裁 补偿" -k 12 --grade A # 只要 A 级证据
python scripts/search.py "降压" --ratio 极高         # 只要极高性价比
python scripts/search.py "押金" --sec 15 --full      # 限定节 + 打印条目全文
python scripts/search.py --item 8.18                 # 按「节.条」直接定位
python scripts/search.py --sec 13 --all              # 整节速览
```

筛选开关：`--grade A|B|C`、`--ratio 极高|高|一般`、`--sec 8,13`、`--kj 金钱|死亡率|时间|自由`、`--free`（不花钱）、`--easy`（不需要毅力）、`--dispute`（只看标了争议的）、`-k N`、`--full`。

Windows 上 `python` 不通时依次试 `py -3`、`python3`，再不行用受管解释器绝对路径 `C:\Users\yuwell\.workbuddy\binaries\python\versions\3.13.12\python.exe`。脚本纯标准库，无依赖。

检索不到时，退回全文 grep：

```bash
grep -rn "关键词" references/book/
```

节与主题的对照、术语表、作者自述的「怎么读」都在 `references/原书README.md`；34 节速览在 `references/章节速览.md`；**只想给用户最省力的一批，直接读 `references/极高性价比清单.md`（114 条）**。

## 第 2 步：整条读完，尤其读「备注」

条目的样子（`--item` 打出来的原文）：

```markdown
### 18. 借钱写清借条，替人担保前先想清楚自己愿不愿意替他还
<!-- 成本标签: 钱=0 时间=少 毅力=否 收益=大 口径=金钱 -->
- 成本：…  - 说人话：…  - 收益：…  - 证据等级：A  - 来源：…  - 备注：…
```

那行 HTML 注释是机器读的成本标签：钱 0/少/多、时间 少/中/多、毅力 否/些/是、收益 大/中/小、口径 死亡率/金钱/时间/自由。分档规则已固化在 `scripts/build_index.py` 的 `ratio_of()`，抄自原书 `tools/lib/book.mjs`，与线上 index.html 一致：成本分 = 钱 + 时间 + 毅力三项权重相加；收益=大且成本分=0 → 极高；收益=大且成本分≤2，或收益=中且成本分=0 → 高；其余 → 一般。

**适用人群、争议、例外都写在「备注」里，只读标题会把条件丢掉。** 标了「⚠争议」的条目要把反方证据也说一句；标了「待核实 / TODO」的别当结论用。

## 第 3 步：排序

1. 先按性价比（极高 > 高 > 一般），同档再按证据等级 A > B > C，最后按与用户处境的贴合度。
2. **不同口径分开列，各排各的**，不合并成一个榜单。
3. 「一般」不等于不该做，只是那笔花销得用户自己掂量。性价比是作者的判断，按书自己的标准只算 C 级，和证据等级是两回事。

## 第 4 步：怎么写答复

结构：

1. **一句话结论**：这件事划不划算、该不该做、第一步是什么。
2. **先做这几条**（3 到 7 条）。每条一到三行：动作（动词开头）、花掉什么、换回什么、证据等级，出处写成「第 8 节第 18 条（借条和担保）」，括号里的词取自条目标题，方便用户自己翻。
3. **别做 / 不用做的**：书里明确说不值得或有反面证据的，单列。
4. **书里没写的**：如实说，不拿常识冒充书的内容。
5. 需要时补一句复查点：什么时候回头再看，或者出现什么信号就改主意。

守则：

- **落到谁身上要说清**。受益人分四档：① 自己；② 配偶和直系亲属；③ 朋友、同事、其他亲属；④ 陌生人。写到第 ④ 档（救陌生人、替人担保、帮人转账）必须把风险面和好处一起写，不能只写好处，也不能写成一律别管。
- **「法律支持你」的事要连过程成本一起说**。只说结果不说过程，等于把胜诉率当收益：要不要打官司、大概多久（一审普通程序 6 个月起、可延长，简易程序 3 个月）、律师费谁掏（律师费不在诉讼费用里，败诉方负担不包括它）。
- **数字照抄条目，一个不改**。置信区间、人群、年份一并留着；HR、RR、OR 旁边就地翻成「低约 28%」，原值不删。条目里没有的数字、症状、机制解读一律不加。
- **口语化**，按没受过专业训练的成年人能一遍读懂来写；专业名词当场用日常话解释一句；法条落到「会摊上什么后果、该怎么做」。来源照原样给，方便核对。
- **语气克制**，不说教，不用感叹号，简体中文。用户不按建议做是他自己的事，不追着劝。
- **政策会变**：第 7、19、21、24、31、32 节里的金额、时限、名单，把正文写的截至日期带上，并提醒自查官方渠道。
- 只给条目「来源」栏里已有的链接，不引知乎、公众号这类二手转述。

## 边界

这本书给的是通用口径，不替代医生、律师、会计。涉及具体病情、具体案件、具体税务的，按书里条目给方向和该找谁，不替专业人士下判断。不给个性化投资建议。

书的观点是作者的，按性价比排序也是作者的判断。用户不同意某一条，把书里的依据摆出来就够了，不辩论。

## 内容与更新

- 正文：`references/book/*.md`（34 节 672 条，取自上游 main 分支）。
- 索引：`data/items.json`，由 `python scripts/build_index.py` 从正文重建；换过正文后必须重跑一次，否则检索用的是旧索引。
- 追上游更新：`python scripts/sync_upstream.py`（浅克隆上游 → 覆盖 `references/book/` 与 `references/原书README.md` → 自动重建索引与两份速查）。需要本机有 `git`；跑之前先看一眼 diff，正文变了再提交。
- 统计口径（2026-10-08 快照）：672 条，A 438 / B 179 / C 55，性价比 极高 114 / 高 304 / 一般 254，标注争议 70 条。数字对不上说明索引过期，重跑 `build_index.py`。

## 装到别的 Agent（格式是通用的，目录不是）

本技能用的是 **Agent Skills 开放标准**（agentskills.io，现由 Linux Foundation 旗下 Agentic AI Foundation 维护）：`SKILL.md` + `scripts/` + `references/`，Claude Code、Codex、Cursor、GitHub Copilot、Gemini CLI、Windsurf、Goose、OpenCode 等都读这一套。

**规范只规定文件格式，不规定放在哪个目录**，所以换个 Agent 用 = 把这一份放到它的技能目录里：

```bash
python scripts/install.py --list          # 看本机各 Agent 目录装了没有
python scripts/install.py                 # 装到 ~/.agents/skills/（跨客户端约定）+ ~/.claude/skills/
python scripts/install.py --all           # 所有识别到的位置都装一份
python scripts/install.py --project <仓库> # 装成项目级， teammates 通过 git 共享
python scripts/install.py --check         # 只做规范自检
python scripts/install.py --zip dist      # 打一个可分发的 zip
```

改过 SKILL.md 之后用 `python scripts/install.py --force` 把改动同步到各处副本。

各家的默认目录：Claude Code `~/.claude/skills/`、Codex `~/.codex/skills/` 或 `~/.agents/skills/`、Cursor `~/.cursor/skills/`、Copilot `~/.copilot/skills/`、Gemini CLI `~/.gemini/skills/`、Windsurf `~/.windsurf/skills/`、OpenCode `~/.config/opencode/skills/`、Goose `~/.config/goose/skills/`。**`~/.agents/skills/` 是跨客户端的公约路径**，除 Claude Code 外各家都读它。

跨 Agent 的两点注意：正文 Markdown 各家照原样加载，但 Claude Code 专有的 `$ARGUMENTS`、`!`shell`` 这类占位符在别家不生效（本技能没用到）；`allowed-tools` 是实验字段，支持程度不一（本技能也没用到）。

## 许可与署名

正文来自 eternity4719/HowToLiveBetter，许可 CC BY 4.0；引用时保留原书出处与「第 X 节第 Y 条」的定位。本技能的脚本与整理稿沿用同一许可。
