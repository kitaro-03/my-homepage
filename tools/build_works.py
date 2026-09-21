#!/usr/bin/env python3
"""
data/works.json から制作物カードのHTMLを組み立てる。

以前はブラウザ側(JavaScript)で組み立てていたが、配信されるHTMLに
作品名や説明が文字として入っている状態にするため、ビルド時に生成する方式へ変更した。
ブログ本文と同じ理由（検索エンジンや広告審査に中身を確実に読ませる）。

JavaScript 側に残っているのは「絞り込み」と「ゲームの起動」だけで、
どちらも生成済みのDOMを操作するだけになっている。
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKS_JSON = ROOT / "data" / "works.json"

# links の kind に応じてボタン頭に出す記号
KIND_MARK = {
    "github": "{ }",
    "itch": "▶",
    "googleplay": "▶",
    "appstore": "",
    "blog": "✎",
    "site": "↗",
}


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def is_external(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def auto_color(seed: str) -> str:
    """
    サムネ画像がないときの背景色を、id の文字列から決める。
    同じ作品は常に同じ色になるので、ビルドし直しても見た目が変わらない。
    """
    h = 0
    for ch in seed:
        h = (h * 31 + ord(ch)) % 360
    return f"linear-gradient(135deg, hsl({h} 62% 42%), hsl({(h + 48) % 360} 58% 30%))"


def initial(title: str) -> str:
    """「（サンプル）〜」のように記号で始まっても、意味のある最初の1文字を拾う。"""
    for ch in title:
        if ch.isalnum():
            return ch
    return "?"


def is_embed(work: dict) -> bool:
    embed = work.get("embed") or {}
    return work.get("type") == "embed" and bool(embed.get("src"))


def validate(works: list[dict]) -> None:
    """壊れたデータのまま公開されないよう、ここで止める。"""
    seen: set[str] = set()
    for i, work in enumerate(works):
        where = f"works[{i}]"
        for key in ("id", "title", "type"):
            if not work.get(key):
                raise SystemExit(f"{where}: '{key}' が必要です")
        if work["type"] not in ("embed", "link"):
            raise SystemExit(f"{where}: type は 'embed' か 'link' です（{work['type']}）")
        if work["id"] in seen:
            raise SystemExit(f"{where}: id '{work['id']}' が重複しています")
        seen.add(work["id"])
        if work["type"] == "embed" and not (work.get("embed") or {}).get("src"):
            raise SystemExit(f"{where}: type が embed なら embed.src が必要です")


def build_badges(work: dict) -> str:
    embed = is_embed(work)
    parts = [
        f'<span class="badge {"badge--playable" if embed else "badge--link"}">'
        f'{"ブラウザで遊べる" if embed else "外部リンク"}</span>'
    ]
    if work.get("status") == "wip":
        parts.append('<span class="badge badge--wip">制作中</span>')
    if work.get("status") == "sample":
        parts.append('<span class="badge badge--sample">サンプル</span>')
    return f'<div class="work-card__badges">{"".join(parts)}</div>'


def build_thumb(work: dict) -> str:
    badges = build_badges(work)
    if work.get("thumbnail"):
        return (
            '<div class="work-card__thumb">'
            f'<img src="{esc(work["thumbnail"])}" alt="" loading="lazy" decoding="async">'
            f"{badges}</div>"
        )
    # 画像がないときはタイトル頭文字のプレースホルダ
    return (
        '<div class="work-card__thumb work-card__thumb--auto" '
        f'style="background: {auto_color(work["id"])}">'
        f'<span aria-hidden="true">{esc(initial(work["title"]))}</span>'
        f"{badges}</div>"
    )


def build_actions(work: dict) -> str:
    parts: list[str] = []
    embed = is_embed(work)

    if embed:
        # JavaScript が無効でも遊べるよう、素のリンクとして出しておく。
        # works.js はこのリンクを横取りして、ページ内ダイアログで開く。
        src = esc(work["embed"]["src"])
        parts.append(
            f'<a class="btn btn--primary btn--sm" href="{src}" data-play="{esc(work["id"])}">'
            "▶ ここで遊ぶ</a>"
        )

    for link in work.get("links") or []:
        url = (link or {}).get("url")
        if not url:
            continue
        primary = (not embed) and link.get("primary")
        mark = KIND_MARK.get(link.get("kind", ""), "↗")
        target = ' target="_blank" rel="noopener noreferrer"' if is_external(url) else ""
        parts.append(
            f'<a class="btn btn--sm {"btn--primary" if primary else "btn--ghost"}" '
            f'href="{esc(url)}"{target}>{esc(mark)} {esc(link.get("label") or "リンク")}</a>'
        )

    if not parts:
        parts.append('<span class="work-card__meta">準備中</span>')
    return f'<div class="work-card__actions">{"".join(parts)}</div>'


def build_card(work: dict) -> str:
    embed = is_embed(work)

    body = [f'<h3 class="work-card__title">{esc(work["title"])}</h3>']
    if work.get("year"):
        body.append(f'<p class="work-card__meta">{esc(work["year"])}</p>')
    body.append(f'<p class="work-card__summary">{esc(work.get("summary", ""))}</p>')

    tags = work.get("tags") or []
    if tags:
        items = "".join(f"<li>{esc(t)}</li>" for t in tags)
        body.append(f'<ul class="tag-list">{items}</ul>')
    body.append(build_actions(work))

    # 埋め込み情報は data 属性で持たせる。works.js はこれを読んでダイアログを開く。
    attrs = ""
    if embed:
        e = work["embed"]
        attrs = (
            f' data-embed-src="{esc(e["src"])}"'
            f' data-embed-aspect="{esc(e.get("aspect") or "16 / 9")}"'
            f' data-embed-controls="{esc(e.get("controls", ""))}"'
            f' data-title="{esc(work["title"])}"'
        )

    return (
        f'<li class="work-card" id="work-{esc(work["id"])}" '
        f'data-type="{"embed" if embed else "link"}"{attrs}>'
        f'{build_thumb(work)}'
        f'<div class="work-card__body">{"".join(body)}</div>'
        "</li>"
    )


def load_works() -> list[dict]:
    try:
        data = json.loads(WORKS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise SystemExit(f"data/works.json の書式が不正です: {err}")
    works = data if isinstance(data, list) else data.get("works", [])
    validate(works)
    return works


def build_cards_html(works: list[dict]) -> str:
    return "\n        ".join(build_card(w) for w in works)
