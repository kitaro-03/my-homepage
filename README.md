# my-homepage

個人ポートフォリオサイト（紹介ページ＋制作物一覧＋開発ブログ）。
GitHub Pages で公開します。

公開URL（Pages有効化後）: `https://kitaro-03.github.io/my-homepage/`

---

## 1. 全体の考え方

ページによって「いつHTMLを作るか」を変えています。

| 部分 | HTMLを作るタイミング | 理由 |
|------|---------------------|------|
| ブログ記事の本文 | **公開前（ビルド時）** | 本文が配信HTMLに文字として入っている必要がある。検索エンジンや広告審査に中身を確実に読ませるため |
| 制作物カード | 表示時（ブラウザ） | `works.json` を1件足すだけで反映させたいから |
| 最新記事のリンク一覧 | 表示時（ブラウザ） | リンクが数行あるだけで、中身の評価に関わらないため |

ブログ本文だけは「JSで後から差し込む」方式を避けています。
自分のブラウザでは正しく見えても、配信されているHTMLは空、という状態になるためです。

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
├── index.html              トップページ（自己紹介＋制作物一覧）※手書き
├── data/
│   ├── works.json          ★ 制作物の一覧データ。ここを編集する
│   └── README.md           works.json の書き方
├── blog/
│   └── _posts/             ★ 記事のMarkdown原稿。ここに .md を置く
├── games/
│   └── sample-dodge/       埋め込み用ミニゲーム（type: embed のサンプル）
├── assets/
│   ├── css/style.css       全ページ共通のスタイル
│   ├── js/works.js         works.json を読んでカードを生成する
│   ├── js/posts.js         posts.json を読んで最新記事リンクを出す
│   └── img/                画像を置く場所
├── tools/
│   ├── build_blog.py       Markdown -> HTML 変換
│   ├── collect_site.py     公開するファイルだけを _site に集める
│   └── templates/          記事ページ・記事一覧のHTMLテンプレート
├── .github/workflows/deploy.yml   ビルドして Pages に公開する
└── .nojekyll
```

### ビルドで生成されるもの（Git管理外）

`.gitignore` に入れてあり、リポジトリには存在しません。

```
blog/index.html                記事一覧
blog/posts/<slug>/index.html   個別記事
data/posts.json                トップページの最新記事リンク用
_site/                         公開されるファイル一式
```

---

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
| `index.html` | `<title>` / `og:title` / `<h1>` / ヘッダーのロゴ / フッターの著作権表記 / GitHubリンク |
| `tools/build_blog.py` | 冒頭の `SITE_NAME` / `SITE_SHORT` / `AUTHOR` / `COPYRIGHT_YEAR` |

`index.html` の該当箇所には `<!-- ▼ 名前は仮置き -->` というコメントを入れてあります。

**制作環境の記載**は `index.html` の `<section class="env-block" id="env">` にあります。
`<dt>見出し</dt><dd>内容</dd>` を1組足すだけで項目が増えます。

---

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

```bash
pip install markdown          # 最初の1回だけ
python3 tools/build_blog.py   # Markdown -> HTML
python3 -m http.server 8000   # http://localhost:8000/
```

`file://` で直接開くとJSONを読み込めないので、必ず簡易サーバー経由で開いてください。

公開されるファイル一式をそのまま確認したいときは:

```bash
python3 tools/build_blog.py && python3 tools/collect_site.py
cd _site && python3 -m http.server 8000
```

JSON を編集したら構文チェックを:

```bash
python3 -c "import json;json.load(open('data/works.json'));print('OK')"
```

---

## 8. GitHub Pages の設定（最初の1回だけ）

1. GitHub のリポジトリ → **Settings** → 左メニューの **Pages**
2. **Source** を `Deploy from a branch` ではなく **`GitHub Actions`** にする
3. `main` に push すると、**Actions** タブでビルドが走る
4. 完了すると `https://kitaro-03.github.io/my-homepage/` で見られる

独自ドメインを後から足す場合は、同じ Pages 設定の **Custom domain** に入力します。
サイト内のリンクはすべて相対パスなので、ドメインが変わっても壊れません。

---

## 9. これから作る予定

- [ ] 制作物カードもビルド時にHTML化するか検討（現状は表示時に生成）
- [ ] RSS / sitemap.xml の出力
- [ ] サムネイル画像の用意（今は頭文字の自動プレースホルダ）
- [ ] 記事へのタグ別一覧ページ
