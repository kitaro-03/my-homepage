#!/usr/bin/env python3
"""
サイト全体をビルドして _site/ に出力する。公開されるのは _site/ の中身だけ。

    pip install markdown
    python3 tools/build.py

やること:
  1. blog/_posts/*.md   -> 記事ページ・記事一覧のHTML
  2. data/works.json    -> 制作物カードのHTML（index.html に差し込む）
  3. 公開するファイルをコピー

リポジトリの中には生成物を一切置かない。
「手で書いたファイル」と「生成されたファイル」が混ざらないようにするため。

公開しないもの:
  blog/_posts/  記事のMarkdown原稿（HTMLに変換済みなので原稿は配信しない）
  tools/        ビルドスクリプト
  .github/      ワークフロー
  *.md          README などの開発用ドキュメント
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import build_blog
import build_works

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"

# index.html の中の、生成したHTMLを差し込む目印
MARKER_WORKS = "<!-- BUILD:WORKS -->"
MARKER_POSTS = "<!-- BUILD:POSTS -->"
MARKER_COUNT = "<!-- BUILD:WORKS_COUNT -->"

# そのままコピーするもの（ディレクトリは中身ごと）
STATIC: list[str] = [
    ".nojekyll",
    "assets",
    "data",
    "games",
]

# 上のディレクトリの中でも、これに当てはまるものは公開しない
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


def build_index(cards_html: str, works_count: int, teaser_html: str) -> str:
    """
    手書きの index.html の目印を、生成したHTMLに置き換える。

    元の index.html は書き換えない。差し替えた結果を _site に書き出すだけなので、
    リポジトリ側の index.html はいつでも手で編集できる状態のまま保たれる。
    """
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    for marker in (MARKER_WORKS, MARKER_POSTS, MARKER_COUNT):
        if marker not in text:
            sys.exit(f"index.html に目印 {marker} がありません。消してしまった可能性があります。")

    text = text.replace(MARKER_WORKS, cards_html)
    text = text.replace(MARKER_POSTS, teaser_html)
    text = text.replace(MARKER_COUNT, f"{works_count} 件")
    return text


def main() -> int:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)

    print("1. ブログ記事を変換")
    posts = build_blog.load_posts()
    build_blog.build(SITE, posts)
    print(f"   記事 {len(posts)} 件")

    print("2. 制作物カードを生成")
    works = build_works.load_works()
    cards = build_works.build_cards_html(works)
    print(f"   制作物 {len(works)} 件")

    print("3. 公開ファイルをコピー")
    (SITE / "index.html").write_text(
        build_index(cards, len(works), build_blog.teaser_html(posts)), encoding="utf-8"
    )
    for name in STATIC:
        src = ROOT / name
        if not src.exists():
            sys.exit(f"公開対象が見つかりません: {name}")
        copy_into(src, SITE / name)

    files = sorted(path for path in SITE.rglob("*") if path.is_file())
    print(f"\n完了: _site に {len(files)} ファイル")
    for path in files:
        print(f"  {path.relative_to(SITE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
