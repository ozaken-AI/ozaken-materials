# プロフィールの画像差し替え

`99_assets/profile-media.json` の各 `src` を変えると、投影プロフィールの画像を差し替えられます。

| 設定名 | 用途 |
| --- | --- |
| `portrait` | 人物写真。初期値は既存のポートレート |
| `lecture` | 講演写真 |
| `community` | イベント・コミュニティ写真 |
| `field` | 活動現場の写真 |

画像を `99_assets/lecture.jpg` などに置き、`"src": "99_assets/lecture.jpg"` と指定します。パスはトップページ基準です。HTTP / HTTPS の画像 URL も使用できます。`src` が空、または画像の読み込みに失敗した枠では、写真の代わりに元の図柄が残ります。

`alt` は実際の写真を説明する文章に更新してください。`objectPosition` は切り抜きの中心です。たとえば `"50% 30%"` は上寄り、`"50% 50%"` は中央になります。

確認用HTMLを作り直す際は設定画像も埋め込むため、追加した写真をそのまま持ち運べます。

単体 HTML を `file://` で開く確認版には、スクリプトより前に `window.OZAKEN_PROFILE_MEDIA = {...};` を埋め込むと、設定ファイルを取得せずに同じ設定を使用できます。写真の埋め込みには PNG / JPEG / WebP などのラスター画像の data URL が使えます。

HTML の枠には `data-profile-media="lecture"` と `data-profile-media-frame` を付け、その内側に `img` を置きます。画像の読み込みが成功した枠だけに `has-media` が付きます。`99_assets/profile-media.js` を `defer` で読み込んでください。
