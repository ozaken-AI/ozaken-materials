# プロフィールの画像差し替え

`99_assets/profile-media.json` の `src` を変えると、投影プロフィールの画像を差し替えられます。提供された写真は加工せず `99_assets/profile/` に保存しています。

| 設定名 | 用途 | 初期素材 |
| --- | --- | --- |
| `portrait` | 冒頭の人物写真 | `profile/hero-stage.jpg` |
| `lecture` | 講演写真 | `profile/lecture-wide.jpg` |
| `community` | コミュニティ写真 | `profile/community-night.jpg` |
| `field` | 活動現場の写真 | 未設定 |
| `course` | 講座画像 | `profile/udemy-ai-agent.png` |
| `public` | 公的活動の写真 | `profile/funabashi.jpg` |
| `policy` | 経済産業省の委員名簿 | `profile/meti-members.png` |

画像を `99_assets/profile/lecture.jpg` などに置き、`"src": "99_assets/profile/lecture.jpg"` と指定します。パスはトップページ基準です。HTTP / HTTPS の画像 URL も使えます。`src` が空、または画像の読み込みに失敗した枠では背景やキャプションが残ります。

`alt` は実際の写真を説明する文章に更新してください。`objectPosition` は CSS の `object-position` で、写真を枠に収める際の切り抜き位置を指定します。たとえば `"50% 30%"` は上寄り、`"50% 50%"` は中央です。画像原本は変更しません。

通常のトップページを開いただけでは、今回追加した写真・講座画像・名簿の6素材は取得しません。`pr` でプロフィールを表示すると、その画面と前後1画面の画像から取得します。以降は移動した画面の前後を読み込み、読み込んだ画像を再利用します。設定 JSON はトップページの初期表示時に取得します。

HTML では枠に `data-profile-media="lecture"` と `data-profile-media-frame` を付け、内側に次のように画像を置きます。画像枠は `.pd-slide` 内に置いてください。

```html
<figure data-profile-media="lecture" data-profile-media-frame>
  <img data-profile-src="99_assets/profile/lecture-wide.jpg"
       data-profile-position="50% 64%"
       alt="講演中の小澤健祐と会場のスクリーン" hidden>
  <!-- 写真が未設定・読込失敗のときに残す図柄 -->
</figure>
```

初期ロードで画像を取得しないよう、`src` の代わりに `data-profile-src` に既定パスを入れます。設定ファイルが取得できない場合やキーが省略された場合は、この既定パスと HTML 内の alt・位置を使います。設定で `"src": ""` を指定すると、その画像枠を意図的に未設定にできます。画像の読み込みが成功した枠だけに `has-media` が付きます。

単体 HTML を `file://` で開く確認版には、スクリプトより前に `window.OZAKEN_PROFILE_MEDIA = {...};` を埋め込むと同じ設定を使用できます。未指定なら JSON を取得せず HTML の既定値を使います。PNG / JPEG / WebP などのラスター画像の data URL にも対応します。`99_assets/profile-media.js` は `defer` で読み込んでください。

経産省名簿の `policy` 枠は、専用CSSで本人の掲載行を表示します。別の名簿画像に差し替える場合は `profile-stage.css` の `.pd-proof-window img` の表示位置も調整してください。
