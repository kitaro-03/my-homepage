# データファイルの書き方

トップページの制作物カードは `data/works.json` から自動生成されます。
**新しい制作物を追加するときは、このファイルの `works` 配列に1件追加するだけ**です。
HTML には一切触りません。

配列の上にあるものほど、ページの上に表示されます。

## 共通のフィールド

| キー | 必須 | 説明 |
|------|------|------|
| `id` | ✔ | 半角英数とハイフン。カードのURL（`#work-xxx`）に使われるので、他と重複しないこと |
| `title` | ✔ | 作品名。カードの見出しになる |
| `summary` | ✔ | 1〜3行の紹介文 |
| `type` | ✔ | `embed`（ページ内で遊べる） か `link`（外部リンクのみ） |
| `year` |  | 制作年。省略可 |
| `status` |  | `released` / `wip`（制作中） / `sample`。バッジとして表示される |
| `tags` |  | 使用技術など。文字列の配列 |
| `thumbnail` |  | サムネ画像のパス（例: `assets/img/foo.png`）。空文字なら自動で色付きの代替画像になる |
| `links` |  | 関連リンクの配列（下記） |

## `links` の書き方

```json
{ "label": "itch.io で遊ぶ", "url": "https://...", "kind": "itch", "primary": true }
```

- `kind` は見た目のアイコン用。`github` / `itch` / `googleplay` / `appstore` / `blog` / `site` が使える（未知の値でも壊れず、汎用アイコンになる）
- `primary: true` を付けたリンクが、カードのメインボタンになる。`type: "link"` の作品には1つ付けておくとよい

## `type: "embed"` のとき

ページ内に iframe で埋め込んで、その場で遊べるようにします。
**軽量なブラウザゲーム向け**です（Unity WebGL のような重いものは `link` にしてください）。

```json
"embed": {
  "src": "games/sample-dodge/index.html",
  "aspect": "4 / 3",
  "controls": "← → キーで移動"
}
```

| キー | 説明 |
|------|------|
| `src` | 埋め込むページのパス。リポジトリ内なら `games/xxx/index.html` のような相対パス |
| `aspect` | 表示比率。`16 / 9`、`4 / 3`、`1 / 1` など。省略時は `16 / 9` |
| `controls` | 操作説明。プレイ画面の下に小さく出る |

ゲームは `games/<作品id>/` にディレクトリごと置く運用にしています。

## `type: "link"` のとき

`embed` は書かず、`links` に外部URLを並べるだけです。
カードには「外部サイトで遊ぶ／見る」ボタンが出ます。

## 編集後の確認

カードはビルド時にHTMLとして生成されます。編集したらビルドして確認してください。

```bash
python3 tools/build.py
```

JSON はカンマ1つで全体が読み込めなくなりますが、その場合はビルドが
エラーで止まります。**壊れたまま公開されることはありません。**

```
data/works.json の書式が不正です: Expecting ',' delimiter: line 7 column 7
works[0]: 'title' が必要です
works[2]: id 'foo' が重複しています
works[1]: type が embed なら embed.src が必要です
```

`id` はカードのURL（`#work-xxx`）とサムネの自動配色に使われるので、
他と重複しない値にしてください。
