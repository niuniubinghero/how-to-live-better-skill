# -*- coding: utf-8 -*-
"""把正文追到上游最新版。

    python scripts/sync_upstream.py [--dry-run]

做三件事：
  1. 浅克隆 github.com/eternity4719/HowToLiveBetter 到临时目录；
  2. 用上游 book/*.md 覆盖 references/book/，用上游 README.md 覆盖 references/原书README.md；
  3. 调 build_index.py 重建 data/items.json 与两份速查。

--dry-run 只下载并列出「哪些节文件变了、条目数增减多少」，不写盘。
需要本机装了 git。
"""
import os, re, io, sys, glob, shutil, subprocess, tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = os.path.join(BASE, 'references', 'book')
README = os.path.join(BASE, 'references', '原书README.md')
UPSTREAM = 'https://github.com/eternity4719/HowToLiveBetter.git'


def count_items(path):
    n = 0
    for f in sorted(glob.glob(os.path.join(path, '*.md'))):
        n += len(re.findall(r'^### \d+\.\s', io.open(f, encoding='utf-8').read(), re.M))
    return n


def main():
    dry = '--dry-run' in sys.argv
    tmp = tempfile.mkdtemp(prefix='hltb-')
    dest = os.path.join(tmp, 'HowToLiveBetter')
    print('克隆上游 ...', UPSTREAM)
    r = subprocess.run(['git', 'clone', '--depth', '1', UPSTREAM, dest],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print(r.stdout, r.stderr, sep='\n')
        sys.exit('克隆失败：本机没有 git，或者连不上 GitHub。正文保持现状不动。')

    src_book = os.path.join(dest, 'book')
    src_files = sorted(glob.glob(os.path.join(src_book, '*.md')))
    old_n, new_n = count_items(BOOK), count_items(src_book)
    changed, added = [], []
    for f in src_files:
        name = os.path.basename(f)
        tgt = os.path.join(BOOK, name)
        if not os.path.exists(tgt):
            added.append(name)
        else:
            a = io.open(tgt, encoding='utf-8').read()
            b = io.open(f, encoding='utf-8').read()
            if a != b:
                changed.append(name)
    gone = [os.path.basename(p) for p in sorted(glob.glob(os.path.join(BOOK, '*.md')))
            if os.path.basename(p) not in {os.path.basename(x) for x in src_files}]

    print(f'\n节文件：新增 {len(added)}、变更 {len(changed)}、上游已删 {len(gone)}')
    for x in added:
        print('  + ' + x)
    for x in changed:
        print('  ~ ' + x)
    for x in gone:
        print('  - ' + x)
    print(f'条目数：{old_n} → {new_n}（{new_n - old_n:+d}）')

    if dry:
        print('\n--dry-run：没有写入任何文件。')
        shutil.rmtree(tmp, ignore_errors=True)
        return
    if not (added or changed or gone):
        print('\n正文没有变化，索引不用重建。')
        shutil.rmtree(tmp, ignore_errors=True)
        return

    for f in src_files:
        shutil.copyfile(f, os.path.join(BOOK, os.path.basename(f)))
    for name in gone:
        os.remove(os.path.join(BOOK, name))
    src_readme = os.path.join(dest, 'README.md')
    if os.path.exists(src_readme):
        shutil.copyfile(src_readme, README)
    print('\n正文已覆盖，重建索引 ...')
    r = subprocess.run([sys.executable, os.path.join(BASE, 'scripts', 'build_index.py')],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(r.stdout or '', r.stderr or '')
    shutil.rmtree(tmp, ignore_errors=True)
    print('同步完成。')


if __name__ == '__main__':
    main()
