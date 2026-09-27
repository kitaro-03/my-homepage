# my-homepage

個人ポートフォリオサイト（紹介ページ＋制作物一覧＋開発ブログ）。
GitHub Pages で公開します。

公開URL（Pages有効化後）: `https://kitaro-03.github.io/my-homepage/`

---

## 1. 全体の考え方

**ページのHTMLは、すべて公開前（ビルド時）に組み立てます。**
配信される `index.html` や記事ページには、作品名・説明・本文が
最初から文字として入っています。

| 部分 | どこから作られるか |
|------|-------------------|
| ブログ記事の本文・一覧 | `blog/_posts/*.md` |
| 制作物カード | `data/works.json` |
| トップの最新記事リンク | `blog/_posts/*.md` |

JavaScript が担当するのは、**絞り込み**と**ゲームのページ内起動**だけです。
どちらも生成済みのHTMLを操作するだけなので、JavaScript が動かなくても
カードは表示され、「ここで遊ぶ」はゲームページへの普通のリンクとして機能します。

### なぜ表示時生成をやめたか

当初は `works.json` をブラウザが読んでカードを組み立てていました。
「JSONを編集すれば即座に反映される」利点があると考えたためですが、これは誤りでした。

Pages の配信元を GitHub Actions にした時点で、`works.json` 自体も
**Actions が集めた成果物として配信される**ようになります。つまり `main` で
JSONを編集しても、配信されるJSONが入れ替わるのは Actions の完了後です。
「ブラウザが実行時に読む」ことと「そのファイルがサーバーに届く」ことは別で、
反映速度はどちらの方式でも変わりません。

利点が無い以上、配信HTMLに中身が入る方を選ばない理由がないため、
ビルド時生成に統一しました。副作用としてJavaScriptも短くなっています
（カード組み立ての処理が不要になったため）。

### なぜ Jekyll ではなく GitHub Actions なのか

GitHub Pages には Jekyll（Markdownを変換する仕組み）が内蔵されていて、
設定なしで使えます。それでも Actions を選んだ理由は3つあります。

1. **`.nojekyll` と両立しない。** このサイトは素のHTML/CSS/JSで、Jekyll に触らせない前提で
   `.nojekyll` を置いています。Jekyll を有効にすると、サイト全体が Jekyll のテンプレート言語
   （Liquid）で処理される対象になります。JavaScript の中に `{{` や `{%` が出てくると
   ビルドが壊れたり、中身が消えたりします。将来の踏みどころを増やしたくありません。
2. **変換したいのは `blog/_posts/` だけ。** サイト全体をJekyllサイトにするのは、
   目的に対して影響範囲が広すぎます。Actions なら「Markdownを変換する」以外は何も変わりません。
3. **手元で同じものを再現できる。** `python3 tools/build_blog.py` を実行すれば、
   Actions と同じ結果が手元にできます。Ruby環境は要りません。

`.nojekyll` は Actions 方式でも残してあります（Actions 経由の配信では Jekyll は動かないので
実質無害ですが、うっかりブランチ配信に戻したときの保険になります）。

---

## 2. ディレクトリ構成

```
.
├── index.html              トップページ ※手書き。カードの差し込み位置に目印がある
├── data/
│   ├── works.json          ★ 制作物の一覧データ。ここを編集する
│   └── README.md           works.json の書き方
├── blog/
│   └── _posts/             ★ 記事のMarkdown原稿。ここに .md を置く
├── games/
│   └── sample-dodge/       埋め込み用ミニゲーム（type: embed のサンプル）
├── assets/
│   ├── css/style.css       全ページ共通のスタイル
│   ├── js/works.js         絞り込みとゲーム起動（カード生成はしない）
│   └── img/                画像を置く場所
├── tools/
│   ├── build.py            ★ ビルドの入口。これ1つを実行する
│   ├── config.py           ★ サイト名・著者名などの設定
│   ├── build_blog.py       Markdown -> HTML
│   ├── build_works.py      works.json -> カードHTML
│   └── templates/          記事ページ・記事一覧のHTMLテンプレート
├── .github/workflows/deploy.yml   ビルドして Pages に公開する
└── .nojekyll
```

### 生成物はリポジトリに置かない

ビルドの出力は `_site/` だけです（`.gitignore` 済み）。
「手で書いたファイル」と「生成されたファイル」が混ざらないようにしてあります。
公開されるのも `_site/` の中身だけで、記事の `.md` 原稿・`tools/`・README は含まれません。

### index.html の目印

`index.html` は手書きのまま保たれ、ビルドはこの目印を置き換えた結果を
`_site/index.html` に書き出します（元ファイルは書き換えません）。

```html
<ul class="works-grid" id="works-grid">
  <!-- BUILD:WORKS -->        ← 制作物カードが入る
</ul>
```

目印は `BUILD:WORKS` / `BUILD:POSTS` / `BUILD:WORKS_COUNT` の3つ。
**消すとビルドが失敗します**（気づかず公開されるのを防ぐため、わざと止めています）。

## 3. 記事を書く

`blog/_posts/` に **Markdownファイルを1つ置くだけ**です。

```
blog/_posts/2026-09-21-unity-progress.md
```

```markdown
---
title: Unityのゲームの進捗
date: 2026-09-21
tags: [Unity, 進捗]
summary: 一覧に出る短い説明（省略すると本文の冒頭から自動で作られる）
---

本文をここに書く。見出しやコードブロックはそのまま使えます。
```

- **ファイル名の先頭の `YYYY-MM-DD-` が日付と並び順**になります
- `YYYY-MM-DD-` の後ろの部分がURLになります（例: `blog/posts/unity-progress/`）
- front matter で必須なのは `title` だけです
- `draft: true` を書くと、その記事は公開されません

書いたら `main` に push すれば、Actions がHTMLに変換して公開します。

### 書く内容についてのルール

このブログは基本的に開発の話が中心ですが、たまにイベントなど
私的な話題を書くこともある、という運用にしています。そのとき1点だけ守ること:

**旅行や外出など「今、家を空けている」とわかる内容は、終わってから書く。**
リアルタイムで書くと、留守にしていることを公開しているのと同じになるため。

（このリポジトリは公開で、一度pushした内容は削除してもgit履歴に残り続けます。
書く前にこの点だけ思い出してください。）

---

## 4. 制作物を追加する

`data/works.json` の `works` 配列に1件追加するだけです。
詳しい書式は [`data/README.md`](data/README.md) を参照してください。

- `"type": "embed"` … `games/<作品id>/` にゲームを置き、ページ内で起動する
- `"type": "link"` … itch.io / Google Play などへのリンクのみ

> Unity WebGL のような重いものは `embed` ではなく `link` にしてください。

---

## 5. 名前を差し替える場所

今は「Kitaro」で仮置きしています。差し替えるのは次の2ファイルだけです。

| ファイル | 箇所 |
|----------|------|
| `tools/config.py` | `SITE_NAME` / `SITE_SHORT` / `AUTHOR` / `GITHUB_USER` / `COPYRIGHT_YEAR` |
| `index.html` | `<title>` / `og:title` / `<h1>` / ヘッダーのロゴ / フッターの著作権表記 / GitHubリンク |

`index.html` の該当箇所には `<!-- ▼ 名前は仮置き -->` というコメントを入れてあります。
（`tools/config.py` はブログ側のページで使われます）

**制作環境の記載**は `index.html` の `<section class="env-block" id="env">` にあります。
`<dt>見出し</dt><dd>内容</dd>` を1組足すだけで項目が増えます。

## 6. 広告（Google AdSense）を入れる

**今はタグを入れていません。枠だけ用意してあります。**

| スロット | 位置 | 想定サイズ |
|----------|------|-----------|
| `top` | ヘッダーのすぐ下 | 728x90 / レスポンシブ |
| `bottom` | フッターの直前 | 728x90 / レスポンシブ |
| `side-left` / `side-right` | 本文の左右（画面幅1280px以上のみ） | 160x600 |

枠は中身が空のあいだ高さ0で畳まれるので、今のレイアウトには影響しません。
URL に `?ads=debug` を付けると点線で可視化されます。

### 入れる手順

1. `index.html` の `<head>` にある AdSense スクリプトのコメントを外し、`ca-pub-XXXX` を差し替える
2. 同じタグを `tools/templates/post.html` と `tools/templates/blog-index.html` にも入れる
3. 表示したい位置の `.ad-slot` の中に `<ins class="adsbygoogle">…</ins>` を貼る

```html
<div class="ad-slot ad-slot--top" data-ad-slot="top" data-ad-label="広告 728x90">
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
       data-ad-slot="1234567890"
       data-ad-format="auto"
       data-full-width-responsive="true"></ins>
  <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>
```

### 守っているルール

- **ゲームの操作エリア（`#game-dialog` の中）には広告を置かない。**
  誤タップを誘発し、AdSense のポリシー違反にもなるため、構造的に分離しています。
- スマホでは左右レールを表示しません（幅が足りず本文を圧迫するため）。

---

## 7. 手元で確認する

ビルドは1コマンドです。公開されるものと完全に同じ `_site/` ができます。

```bash
pip install markdown        # 最初の1回だけ
python3 tools/build.py      # -> _site/ に出力
cd _site && python3 -m http.server 8000
# http://localhost:8000/
```

`index.html` をそのまま開いてもカードは出ません（目印のままなので）。
確認は必ず `_site` 側を見てください。

データが壊れているときは、ビルドがエラーで止まります。
公開されるのはビルドが成功したときだけなので、壊れたまま公開されることはありません。

```
works[0]: 'title' が必要です
data/works.json の書式が不正です: Expecting ',' delimiter: line 7 column 7
```

## 8. GitHub Pages の設定（最初の1回だけ）

1. GitHub のリポジトリ → **Settings** → 左メニューの **Pages**
2. **Source** を `Deploy from a branch` ではなく **`GitHub Actions`** にする
3. `main` に push すると、**Actions** タブでビルドが走る
4. 完了すると `https://kitaro-03.github.io/my-homepage/` で見られる

独自ドメインを後から足す場合は、同じ Pages 設定の **Custom domain** に入力します。
サイト内のリンクはすべて相対パスなので、ドメインが変わっても壊れません。

---

## 9. これから作る予定

- [ ] RSS / sitemap.xml の出力
- [ ] サムネイル画像の用意（今は頭文字の自動プレースホルダ）
- [ ] 記事へのタグ別一覧ページ
