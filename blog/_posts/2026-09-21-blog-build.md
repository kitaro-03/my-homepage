---
title: ブログをMarkdownからビルドする仕組みにした
date: 2026-09-21
tags: [サイト制作, GitHub Actions]
summary: 記事をMarkdownで書き、GitHub Actions でHTMLに変換してから公開する形にしました。その理由と構成のメモ。
---

ブログ部分を、Markdown で書いて公開時にHTMLへ変換する形にしました。

## なぜ変換してから配信するのか

本文をJavaScriptで後から差し込む方式だと、配信されるHTMLの中身が空になります。
自分のブラウザでは正しく見えるので気づきにくいのですが、
クローラや審査の環境によっては「中身のないページ」として扱われる可能性があります。

そのため、本文は**配信されるHTMLの中に文字として入っている**状態にしました。

## 書き方

`blog/_posts/` に、こういうファイルを置くだけです。

```
blog/_posts/2026-09-21-example.md
```

```markdown
---
title: 記事のタイトル
date: 2026-09-21
tags: [Unity, 進捗]
---

本文をここに書く。
```

ファイル名の先頭の日付がそのまま記事の日付と並び順になります。

## コードの表示確認

```python
def hello(name: str) -> str:
    return f"hello, {name}"
```

| 項目 | 内容 |
|------|------|
| 変換 | Python の markdown |
| 実行 | GitHub Actions |
| 公開 | GitHub Pages |

> 引用の表示確認。
