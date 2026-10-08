# -*- coding: utf-8 -*-
"""把这个技能装到别的 AI Agent（或校验它是否符合通用规范）。

Agent Skills 是开放标准（agentskills.io）：SKILL.md + scripts/ + references/ 各家通用，
但**规范不规定放在哪个目录**，每个客户端自己挑目录。所以「一份内容、多处落地」要自己复制或建链接。

    python scripts/install.py --list                 # 看看本机有哪些 Agent 目录、装了没有
    python scripts/install.py                        # 装到两个通用位置（默认）
    python scripts/install.py --all                  # 装到所有识别到的位置
    python scripts/install.py --target claude,codex  # 只装指定几家
    python scripts/install.py --project D:/myrepo    # 装成项目级：<项目>/.agents/skills/
    python scripts/install.py --link                 # 用 junction/软链，不占第二份空间
    python scripts/install.py --check                # 只做规范自检，不写盘
    python scripts/install.py --zip dist             # 另打一个可分发的 zip

默认装的两处（覆盖几乎所有客户端）：
  ~/.agents/skills/   Codex、ChatGPT、Cursor、GitHub Copilot、Gemini CLI、Windsurf 都读它
  ~/.claude/skills/   Claude Code 不读 .agents，得单独放一份
"""
import os, re, io, sys, json, shutil, zipfile, argparse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = os.path.basename(BASE)
HOME = os.path.expanduser('~')

# 各家客户端的技能目录（用户级 / 项目级）。项目级一律用 .agents/skills/ 这一跨客户端约定，
# 只有 Claude Code 是例外，得单独放 .claude/skills/。
TARGETS = [
    # key, 说明, 用户级路径, 项目级相对路径
    ('agents',  '跨客户端约定（Codex/Cursor/Copilot/Gemini/Windsurf 都读）',
     os.path.join(HOME, '.agents', 'skills'), '.agents/skills'),
    ('claude',  'Claude Code',
     os.path.join(HOME, '.claude', 'skills'), '.claude/skills'),
    ('codex',   'OpenAI Codex',
     os.path.join(HOME, '.codex', 'skills'), '.codex/skills'),
    ('cursor',  'Cursor',
     os.path.join(HOME, '.cursor', 'skills'), '.cursor/skills'),
    ('copilot', 'GitHub Copilot / VS Code',
     os.path.join(HOME, '.copilot', 'skills'), '.github/skills'),
    ('gemini',  'Gemini CLI',
     os.path.join(HOME, '.gemini', 'skills'), '.gemini/skills'),
    ('windsurf', 'Windsurf',
     os.path.join(HOME, '.windsurf', 'skills'), '.agents/skills'),
    ('opencode', 'OpenCode',
     os.path.join(HOME, '.config', 'opencode', 'skills'), '.opencode/skills'),
    ('goose',   'Goose',
     os.path.join(HOME, '.config', 'goose', 'skills'), None),
    ('workbuddy', 'WorkBuddy（本技能当前所在处）',
     os.path.join(HOME, '.workbuddy', 'skills'), '.workbuddy/skills'),
]
DEFAULT = ('agents', 'claude')


# ---------- 规范自检 ----------
def check():
    errs, warns = [], []
    path = os.path.join(BASE, 'SKILL.md')
    if not os.path.exists(path):
        return ['缺少 SKILL.md'], warns
    text = io.open(path, encoding='utf-8').read()
    m = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n', text, re.S)
    if not m:
        return ['SKILL.md 缺少 YAML frontmatter'], warns
    fm = {}
    for line in m.group(1).split('\n'):
        mm = re.match(r'^([A-Za-z_-]+):\s*(.*)$', line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip()
    if 'name' not in fm:
        errs.append('frontmatter 缺 name')
    else:
        n = fm['name']
        if len(n) > 64:
            errs.append(f'name 超过 64 字符（{len(n)}）')
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', n):
            errs.append('name 只能是小写字母、数字、连字符，且不能以连字符开头/结尾或有连续连字符')
        if n != NAME:
            errs.append(f'name（{n}）必须和目录名（{NAME}）一致')
    if 'description' not in fm:
        errs.append('frontmatter 缺 description')
    elif not (1 <= len(fm['description']) <= 1024):
        errs.append(f'description 长度须在 1–1024（{len(fm["description"])}）')
    if len(fm.get('compatibility', '')) > 500:
        errs.append('compatibility 超过 500 字符')
    body = text[m.end():]
    lines = body.count('\n') + 1
    if lines > 500:
        warns.append(f'SKILL.md 正文 {lines} 行，规范建议 < 500 行')
    for extra in fm:
        if extra not in ('name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'):
            warns.append(f'frontmatter 字段 {extra} 不在规范字段里（各客户端通常会忽略，WorkBuddy 用它做管理）')
    # 正文里引用的文件是否真的存在
    for ref in set(re.findall(r'`?((?:scripts|references|assets)/[^\s`()（）]+)', body)):
        if '*' in ref or '?' in ref:      # 通配符引用不逐个检查
            continue
        if not os.path.exists(os.path.join(BASE, ref.replace('/', os.sep))):
            warns.append(f'正文引用了不存在的文件：{ref}')
    return errs, warns


# ---------- 安装 ----------
def deploy(dst, link, force=False):
    dst = os.path.join(dst, NAME) if os.path.basename(dst) != NAME else dst
    if os.path.isdir(dst) or os.path.islink(dst):
        if not force:
            return '已存在，跳过', dst
        if link:
            try:                                  # 链接/联结只摘链接，不动内容
                os.remove(dst) if os.path.islink(dst) else os.rmdir(dst)
            except OSError:
                pass
            if not os.path.exists(dst):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                return make_link(BASE, dst) + '(覆盖)', dst
        # 覆盖式复制：只覆盖同名文件、补上新文件，不做任何删除（也就不触发删除守卫）
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        copy(BASE, dst, dirs_exist_ok=True)
        return '复制(覆盖)', dst
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    kind = make_link(BASE, dst) if link else copy(BASE, dst)
    return (kind + '(覆盖)' if force else kind), dst


def make_link(src, dst):
    """先试软链；Windows 上退到目录联结（mklink /J），再不行就复制。"""
    try:
        os.symlink(src, dst, target_is_directory=True)
        return '软链'
    except (OSError, NotImplementedError):
        pass
    if os.name == 'nt' and os.system(f'cmd /c mklink /J "{dst}" "{src}" >nul') == 0:
        return '目录联结'
    copy(src, dst)
    return '链接失败→复制'


def copy(src, dst, dirs_exist_ok=False):
    def ignore(d, names):
        return {n for n in names
                if os.path.isdir(os.path.join(d, n)) and n in ('__pycache__', '.git')}
    shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=dirs_exist_ok)
    return '复制'


def main():
    ap = argparse.ArgumentParser(description='把 how-to-live-better 装到各 AI Agent 的技能目录')
    ap.add_argument('--list', action='store_true', help='只列出本机各目录与安装状态')
    ap.add_argument('--check', action='store_true', help='只做 Agent Skills 规范自检')
    ap.add_argument('--all', action='store_true', help='装到所有识别到的位置')
    ap.add_argument('--target', help='逗号分隔，如 claude,codex,cursor')
    ap.add_argument('--project', help='项目根目录，装成项目级技能')
    ap.add_argument('--link', action='store_true', help='用软链/目录联结，不复制（约 4.8 MB）')
    ap.add_argument('--force', action='store_true', help='已存在就覆盖，用于把改动同步到各处的副本')
    ap.add_argument('--zip', help='额外打一个分发用 zip 到指定目录')
    a = ap.parse_args()

    errs, warns = check()
    print('== 规范自检（agentskills.io） ==')
    if errs:
        for e in errs:
            print('  [错误] ' + e)
    else:
        print('  通过：SKILL.md 符合 Agent Skills 规范')
    for w in warns:
        print('  [提示] ' + w)

    if a.zip:
        os.makedirs(a.zip, exist_ok=True)
        zp = os.path.join(a.zip, f'{NAME}.zip')
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(BASE):
                dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git')]
                for f in files:
                    p = os.path.join(root, f)
                    z.write(p, os.path.relpath(p, os.path.dirname(BASE)))
        print(f'\n分发包：{zp}（{os.path.getsize(zp)/1048576:.1f} MB）')

    if a.check:
        sys.exit(1 if errs else 0)

    if a.project:
        keys = ['agents', 'claude']
        print('\n== 项目级安装：%s ==' % a.project)
        for k, desc, _u, proj in TARGETS:
            if k in keys and proj:
                dst = os.path.join(a.project, proj, NAME)
                if os.path.isdir(dst):
                    print(f'  {desc:<34} 已存在，跳过')
                    continue
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                copy(BASE, dst)
                print(f'  {desc:<34} 已装到 {proj}/{NAME}/')
        return

    keys = [k for k, *_ in TARGETS] if a.all else (
        [x.strip() for x in a.target.split(',')] if a.target else list(DEFAULT))
    print('\n== 用户级安装 ==')
    for k, desc, user, _p in TARGETS:
        if a.list:                       # --list 只报告，不写盘
            dst = os.path.join(user, NAME)
            state = '已安装' if os.path.isdir(dst) else '未安装'
            parent = '' if os.path.isdir(os.path.dirname(user)) else '（该 Agent 目录不存在，推测未安装此工具）'
            print(f'  {desc:<34} {state:<6} {dst} {parent}')
            continue
        if k not in keys:
            continue
        parent_exists = os.path.isdir(os.path.dirname(user))
        status, dst = deploy(user, a.link, a.force)
        mark = '' if parent_exists else '（该 Agent 目录不存在，推测未安装此工具）'
        print(f'  {desc:<34} {status:<8} {dst} {mark}')
    if a.list:
        return
    print('\n装完重启一下对应 Agent 的会话，让它重新扫描技能目录。')
    if not a.link:
        print('提示：不想占多份空间，下次加 --link（Windows 上会退化成目录联结）。')


if __name__ == '__main__':
    main()
