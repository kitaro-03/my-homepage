# my-homepage

個人ポートフォリオサイト（紹介ページ＋制作物一覧＋開発ブログ）。
GitHub Pages で公開する前提の、**ビルド不要の静的サイト**です。

公開URL（Pages有効化後）: `https://kitaro-03.github.io/my-homepage/`

---

## 1. なぜこの構成なのか

GitHub Pages はファイルをそのまま配信するだけで、サーバー側の処理は動きません。
そのため次の方針にしています。

| 方針 | 理由 |
|------|------|
| フレームワークなし、素の HTML / CSS / JS | ビルド工程がないので、push した瞬間に反映される。壊れどころが少ない |
| 制作物は `data/works.json` に集約 | 作品追加が「JSONに1件足す」だけで済む。HTMLを触らない |
| カードはブラウザ側で組み立て | ビルドサーバーが要らない。GitHub上でJSONを直接編集しても反映される |
| 外部CDN・Webフォントを使わない | 表示が外部サービスの生死に依存しない。速い |

---

## 2. ディレクトリ構成

```
.
├── index.html              トップページ（自己紹介＋制作物一覧）
├── blog/
│   └── index.html          開発ブログ（※これから作る。今は受け皿だけ）
├── data/
│   ├── works.json          ★ 制作物の一覧データ。ここを編集する
│   └── README.md           works.json の書き方
├── games/
│   └── sample-dodge/       埋め込み用ミニゲーム（type: embed のサンプル）
├── assets/
│   ├── css/style.css       全ページ共通のスタイル
│   ├── js/works.js         works.json を読んでカードを生成する
│   └── img/                サムネイル画像を置く場所
└── .nojekyll               GitHub Pages の Jekyll 処理を無効化する
```

`.nojekyll` は、`_` で始まるファイル名が無視されるなどの
Jekyll の余計な変換を止めるための空ファイルです。消さないでください。

---

## 3. 制作物を追加する

`data/works.json` の `works` 配列に1件追加するだけです。詳しい書式は
[`data/README.md`](data/README.md) を参照してください。

### ブラウザで遊べるもの（`type: "embed"`）

1. `games/<作品id>/` にゲーム一式を置く
2. `works.json` に追記する

```json
{
  "id": "my-game",
  "title": "作品名",
  "summary": "説明",
  "type": "embed",
  "tags": ["JavaScript"],
  "embed": { "src": "games/my-game/index.html", "aspect": "4 / 3", "controls": "← → で移動" }
}
```

カードに「▶ ここで遊ぶ」ボタンが出て、ページ内のダイアログで起動します。

### 外部リンクのみ（`type: "link"`）

itch.io（Unity製ゲーム）、Google Play、外部サイトなど。

```json
{
  "id": "my-unity-game",
  "title": "作品名",
  "summary": "説明",
  "type": "link",
  "tags": ["Unity"],
  "links": [{ "label": "itch.io で遊ぶ", "url": "https://...", "kind": "itch", "primary": true }]
}
```

> Unity WebGL のような重いものは、`embed` ではなく `link` にしてください。
> ページの読み込みが極端に重くなります。

---

## 4. 広告（Google AdSense）を入れる

**今はタグを入れていません。枠だけ用意してあります。**

### 確保してある位置

| スロット | 位置 | 想定サイズ |
|----------|------|-----------|
| `top` | ヘッダーのすぐ下 | 728x90 / レスポンシブ |
| `bottom` | フッターの直前 | 728x90 / レスポンシブ |
| `side-left` / `side-right` | 本文の左右（画面幅1280px以上のみ） | 160x600 |

枠は**中身が空のあいだ高さ0で畳まれる**ので、今のレイアウトには影響しません。

### 位置を目で確認する

URL に `?ads=debug` を付けると、枠が点線で可視化されます。

```
http://localhost:8000/?ads=debug
```

### 実際に入れる手順

1. `index.html` の `<head>` にある AdSense スクリプトのコメントを外し、`ca-pub-XXXX` を自分のIDに差し替える
2. 入れたい位置の `.ad-slot` の中に `<ins class="adsbygoogle">…</ins>` を貼る

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

- **ゲームの操作エリア（プレイ用ダイアログ `#game-dialog` の中）には広告を置かない。**
  操作中の誤タップを誘発し、AdSense のポリシー違反にもなるため、構造的に分離しています。
- スマホでは左右レールを表示しません（幅が足りず、本文を圧迫するため）。

---

## 5. ローカルで確認する

`file://` で直接開くと、ブラウザの制約で `data/works.json` を読み込めません
（カード部分にその旨のエラーが出ます）。簡易サーバーを立ててください。

```bash
python3 -m http.server 8000
# → http://localhost:8000/
```

JSON を編集したら構文チェックを:

```bash
python3 -c "import json;json.load(open('data/works.json'));print('OK')"
```

---

## 6. GitHub Pages で公開する

1. GitHub のリポジトリ → **Settings** → **Pages**
2. **Source** で `Deploy from a branch` を選ぶ
3. Branch に `main`、フォルダは `/ (root)` を指定して Save
4. 1〜2分待つと `https://kitaro-03.github.io/my-homepage/` で見られる

独自ドメインを後から足す場合は、同じ Pages 設定の **Custom domain** に
ドメインを入力します（リポジトリ直下に `CNAME` ファイルが自動生成されます）。
サイト内のリンクはすべて相対パスで書いてあるので、ドメインが変わっても壊れません。

---

## 7. これから作る予定

- [ ] ブログの記事一覧を `data/posts.json` からの自動生成にする
- [ ] 個別記事ページのテンプレート
- [ ] サムネイル画像の用意（今は頭文字の自動プレースホルダ）
- [ ] プロフィール画像・紹介文の差し替え（`index.html` の `TODO` コメント箇所）
