#!/usr/bin/env python3
"""
blog/_posts/*.md を読んで、記事ページと記事一覧のHTMLを組み立てる。

なぜビルドするのか:
  ブログ本文は「配信されるHTMLの中に文字として入っている」必要がある。
  JavaScriptで後から差し込む方式だと、クローラや審査の環境によっては
  中身が空のページとして読まれてしまうため。

このファイルは tools/build.py から呼ばれるモジュール。単体では実行しない。
"""

from __future__ import annotations

import html
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import config

try:
    import markdown
except ImportError:
    sys.exit("markdown がありません。`pip install markdown` を実行してください。")

ROOT = Path(__file__).resolve().parent.parent
POSTS_SRC = ROOT / "blog" / "_posts"
TEMPLATES = Path(__file__).resolve().parent / "templates"

FILENAME_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$")

MD_EXTENSIONS = ["fenced_code", "tables", "sane_lists", "nl2br", "attr_list"]


@dataclass
class Post:
    slug: str
    title: str
    published: date
    summary: str
    tags: list[str] = field(default_factory=list)
    body_html: str = ""

    @property
    def url(self) -> str:
        """サイトルートからの相対パス。"""
        return f"blog/posts/{self.slug}/"

    @property
    def date_iso(self) -> str:
        return self.published.isoformat()

    @property
    def date_display(self) -> str:
        return self.published.strftime("%Y年%m月%d日")


# ---------------------------------------------------------------------------
# 原稿の読み込み
# ---------------------------------------------------------------------------
def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    """
    先頭の --- ... --- を key: value の辞書として取り出す。

    YAML をフルに解釈するのはやりすぎなので、このサイトで使う範囲
    （1行の key: value のみ）に絞った軽い実装にしている。
    """
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    meta: dict[str, str] = {}
    for line in parts[1].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip().lower()] = value.strip().strip('"').strip("'")
    return meta, parts[2].lstrip("\n")


def split_tags(raw: str) -> list[str]:
    """tags: [Unity, 進捗] / tags: Unity, 進捗 のどちらでも受ける。"""
    raw = raw.strip().lstrip("[").rstrip("]")
    return [t.strip() for t in raw.split(",") if t.strip()]


def first_paragraph(md_body: str, limit: int = 110) -> str:
    """summary が書かれていないとき、本文の冒頭から要約を作る。"""
    for block in md_body.split("\n\n"):
        text = block.strip()
        if not text or text.startswith(("#", "!", "|", ">", "```", "-", "*")):
            continue
        text = re.sub(r"[*_`\[\]]|\(https?://[^)]*\)", "", text)
        text = " ".join(text.split())
        return text[:limit] + ("…" if len(text) > limit else "")
    return ""


def load_post(path: Path) -> Post | None:
    raw = path.read_text(encoding="utf-8")
    meta, body_md = parse_front_matter(raw)

    # ファイル名 YYYY-MM-DD-slug.md から日付とslugを取る
    match = FILENAME_RE.match(path.stem)
    if match:
        y, m, d, slug = match.groups()
        published = date(int(y), int(m), int(d))
    else:
        slug = path.stem
        published = date.fromtimestamp(path.stat().st_mtime)

    # front matter に書かれていればそちらを優先する
    if meta.get("date"):
        try:
            published = date.fromisoformat(meta["date"])
        except ValueError:
            print(f"  ! {path.name}: date の書式が不正なのでファイル名の日付を使います")
    slug = meta.get("slug") or slug

    if meta.get("draft", "").lower() in ("true", "yes", "1"):
        print(f"  - {path.name} は下書きなのでスキップ")
        return None

    converter = markdown.Markdown(extensions=MD_EXTENSIONS)
    return Post(
        slug=slug,
        title=meta.get("title") or slug,
        published=published,
        summary=meta.get("summary") or first_paragraph(body_md),
        tags=split_tags(meta.get("tags", "")),
        body_html=converter.convert(body_md),
    )


def load_posts() -> list[Post]:
    if not POSTS_SRC.is_dir():
        sys.exit(f"{POSTS_SRC} がありません。")

    posts: list[Post] = []
    for path in sorted(POSTS_SRC.glob("*.md")):
        post = load_post(path)
        if post:
            posts.append(post)
            print(f"  + {path.name} -> {post.url}")

    posts.sort(key=lambda p: (p.published, p.slug), reverse=True)

    slugs = [p.slug for p in posts]
    duplicates = {s for s in slugs if slugs.count(s) > 1}
    if duplicates:
        sys.exit(f"記事のURL(slug)が重複しています: {duplicates}")
    return posts


# ---------------------------------------------------------------------------
# HTMLの生成
# ---------------------------------------------------------------------------
def render(template_name: str, values: dict[str, str]) -> str:
    """{{KEY}} を values[KEY] に置き換えるだけの、ごく単純なテンプレート。"""
    text = (TEMPLATES / template_name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    leftover = set(re.findall(r"\{\{[A-Z_]+\}\}", text))
    if leftover:
        sys.exit(f"{template_name}: 未置換のプレースホルダが残っています {leftover}")
    return text


def tag_list_html(tags: list[str]) -> str:
    if not tags:
        return ""
    items = "".join(f"<li>{html.escape(t)}</li>" for t in tags)
    return f'<ul class="tag-list">{items}</ul>'


def common_values(root_prefix: str) -> dict[str, str]:
    """全テンプレート共通の値。root_prefix はサイトルートへの相対パス。"""
    return {
        "ROOT": root_prefix,
        "SITE_NAME": html.escape(config.SITE_NAME),
        "SITE_SHORT": html.escape(config.SITE_SHORT),
        "AUTHOR": html.escape(config.AUTHOR),
        "YEAR": config.COPYRIGHT_YEAR,
    }


def post_page(post: Post, newer: Post | None, older: Post | None) -> str:
    nav = []
    if newer:
        nav.append(f'<a class="btn btn--sm btn--ghost" href="../{newer.slug}/">← {html.escape(newer.title)}</a>')
    if older:
        nav.append(f'<a class="btn btn--sm btn--ghost" href="../{older.slug}/">{html.escape(older.title)} →</a>')

    values = common_values("../../../")
    values.update({
        "TITLE": html.escape(post.title),
        "SUMMARY": html.escape(post.summary),
        "DATE_ISO": post.date_iso,
        "DATE_DISPLAY": post.date_display,
        "TAGS": tag_list_html(post.tags),
        "CONTENT": post.body_html,
        "POST_NAV": "".join(nav),
    })
    return render("post.html", values)


def blog_index_page(posts: list[Post]) -> str:
    if posts:
        rows = "\n".join(
            f'        <li><a href="posts/{p.slug}/">'
            f'<time datetime="{p.date_iso}">{p.date_iso}</time>'
            f'<span><span class="post-list__title">{html.escape(p.title)}</span>'
            f'<span class="post-list__summary">{html.escape(p.summary)}</span></span>'
            "</a></li>"
            for p in posts
        )
        list_html = f'<ul class="post-list">\n{rows}\n      </ul>'
    else:
        list_html = '<p class="works-status">まだ記事がありません。</p>'

    values = common_values("../")
    values.update({"POST_LIST": list_html, "POST_COUNT": str(len(posts))})
    return render("blog-index.html", values)


def build(site: Path, posts: list[Post]) -> None:
    """記事ページと記事一覧を site 以下に書き出す。"""
    for i, post in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        out_dir = site / "blog" / "posts" / post.slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(post_page(post, newer, older), encoding="utf-8")

    blog_dir = site / "blog"
    blog_dir.mkdir(parents=True, exist_ok=True)
    (blog_dir / "index.html").write_text(blog_index_page(posts), encoding="utf-8")


def teaser_html(posts: list[Post]) -> str:
    """トップページの「最近書いたもの」に差し込むリスト。"""
    if not posts:
        return '<li><span class="work-card__meta">まだ記事がありません。</span></li>'
    return "\n        ".join(
        f'<li><a href="{p.url}">'
        f'<time datetime="{p.date_iso}">{p.date_iso}</time>'
        f'<span class="post-list__title">{html.escape(p.title)}</span></a></li>'
        for p in posts[: config.TEASER_COUNT]
    )
