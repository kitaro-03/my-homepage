#!/usr/bin/env python3
"""
公開するファイルだけを _site/ に集める。

リポジトリには「公開したくないもの」も入っている:
  - blog/_posts/   記事のMarkdown原稿（HTMLに変換済みなので原稿は配信しない）
  - tools/         ビルドスクリプト
  - .github/       ワークフロー
  - *.md           README などの開発用ドキュメント

「何を除くか」ではなく「何を公開するか」を明示的に列挙する方式にしている。
除外を書き忘れて意図しないファイルが公開される事故を防ぐため。

使い方:
  python3 tools/build_blog.py && python3 tools/collect_site.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"

# 公開するもの。ディレクトリを書くと中身ごとコピーされる。
PUBLISH: list[str] = [
    "index.html",
    ".nojekyll",
    "assets",
    "data",
    "games",
    "blog",
]

# 上のディレクトリの中でも、これに当てはまるものは公開しない。
EXCLUDE_NAMES = {"_posts", "__pycache__", ".DS_Store"}
EXCLUDE_SUFFIXES = {".md", ".py", ".pyc"}


def keep(path: Path) -> bool:
    if path.name in EXCLUDE_NAMES:
        return False
    if path.is_file() and path.suffix.lower() in EXCLUDE_SUFFIXES:
        return False
    return True


def copy_into(src: Path, dst: Path) -> int:
    """keep() を通ったものだけを再帰的にコピーし、コピーしたファイル数を返す。"""
    if not keep(src):
        return 0
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return 1
    count = 0
    dst.mkdir(parents=True, exist_ok=True)
    for child in sorted(src.iterdir()):
        count += copy_into(child, dst / child.name)
    return count


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    missing = [name for name in PUBLISH if not (ROOT / name).exists()]
    if missing:
        sys.exit(
            f"公開対象が見つかりません: {missing}\n"
            "ブログの生成物が無い場合は、先に python3 tools/build_blog.py を実行してください。"
        )

    total = 0
    for name in PUBLISH:
        total += copy_into(ROOT / name, OUT / name)

    print(f"_site に {total} ファイルを集めました")
    for path in sorted(OUT.rglob("*")):
        if path.is_file():
            print(f"  {path.relative_to(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
