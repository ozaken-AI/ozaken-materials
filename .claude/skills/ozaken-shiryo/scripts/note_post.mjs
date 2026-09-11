// note_export.py が出した下書きを、note の「下書き」として保存する（公開はしない）。
//
//   1) 一度だけ、手元のPCでログインした状態を保存する（ブラウザが開くので手で入る）
//        node note_post.mjs --login ~/note-state.json
//   2) 下書きを note に入れる
//        NOTE_STATE=~/note-state.json node note_post.mjs note_drafts/what-is-agi
//      --dry-run を付けると、ブラウザを開かずに何を入れるかだけ表示する
//
// **未検証。** note に公式の投稿APIは無く、エディタの画面の作りは予告なく変わる。
// だからこの台本は、必ず「下書き保存」で止まり、公開ボタンには触らない。
// 画面の作りが変わって途中で止まったら、article.md を手で貼るほうが早い。
// ログイン状態のファイル（Cookie）は鍵と同じ。リポジトリにも、共有にも置かない。
import fs from 'fs';
import path from 'path';

const args = process.argv.slice(2);
const dry = args.includes('--dry-run');
const loginAt = args.indexOf('--login');
const dir = args.find(a => !a.startsWith('--') && (loginAt < 0 || args[loginAt + 1] !== a));

let chromium;
try { ({ chromium } = await import('playwright-core')); }
catch (e) { console.error('playwright-core が見つかりません。npm i playwright-core'); process.exit(1); }
const exe = process.env.CHROMIUM || '/opt/pw-browsers/chromium';

if (loginAt >= 0) {
  const out = args[loginAt + 1] || 'note-state.json';
  const b = await chromium.launch({ executablePath: exe, headless: false });
  const ctx = await b.newContext();
  const p = await ctx.newPage();
  await p.goto('https://note.com/login');
  console.log('ブラウザでログインしてください。ログインできたら、このターミナルで Enter を押します。');
  await new Promise(r => process.stdin.once('data', r));
  await ctx.storageState({ path: out });
  console.log('保存しました:', out, '（このファイルは鍵と同じ扱い。共有しない）');
  await b.close();
  process.exit(0);
}

if (!dir) { console.error('使い方: NOTE_STATE=state.json node note_post.mjs <下書きのディレクトリ> [--dry-run]'); process.exit(1); }
const md = fs.readFileSync(path.join(dir, 'article.md'), 'utf8');
const meta = JSON.parse(fs.readFileSync(path.join(dir, 'meta.json'), 'utf8'));
const title = process.env.NOTE_TITLE || meta.title_candidates[0];

// article.md を、エディタに入れる単位（段落）に割る
const blocks = [];
for (const line of md.split('\n')) {
  const m = line.match(/^!\[(.*?)\]\((.*?)\)$/);
  if (m) { blocks.push({ kind: 'image', file: path.join(dir, m[2]), alt: m[1] }); continue; }
  if (/^##\s/.test(line)) { blocks.push({ kind: 'h2', text: line.replace(/^##\s+/, '') }); continue; }
  if (/^###\s/.test(line)) { blocks.push({ kind: 'h3', text: line.replace(/^###\s+/, '') }); continue; }
  if (/^>\s?/.test(line)) { blocks.push({ kind: 'quote', text: line.replace(/^>\s?/, '') }); continue; }
  if (line.trim() === '---') { blocks.push({ kind: 'rule' }); continue; }
  if (line.trim()) blocks.push({ kind: 'p', text: line });
}
console.log('題:', title);
console.log('段落 %d / 画像 %d / タグ %s', blocks.length, blocks.filter(b => b.kind === 'image').length, meta.hashtags.join(' '));
if (dry) { blocks.slice(0, 12).forEach(b => console.log(' ', b.kind, (b.text || b.file || '').slice(0, 60))); process.exit(0); }

const state = process.env.NOTE_STATE;
if (!state || !fs.existsSync(state)) { console.error('NOTE_STATE にログイン状態のファイルを指定してください（--login で作れます）'); process.exit(1); }

const b = await chromium.launch({ executablePath: exe, headless: !process.env.HEADED });
const ctx = await b.newContext({ storageState: state, viewport: { width: 1280, height: 900 } });
const p = await ctx.newPage();
await p.goto('https://note.com/notes/new', { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(3000);
if (/login/.test(p.url())) { console.error('ログインが切れています。--login で取り直してください'); await b.close(); process.exit(1); }

// 題
const titleBox = p.locator('textarea[placeholder*="タイトル"], [data-placeholder*="タイトル"], textarea').first();
await titleBox.click();
await p.keyboard.type(title, { delay: 5 });

// 本文。ProseMirror 系のエディタは、行頭の "## " や "> " を見出し・引用に変える
const body = p.locator('.ProseMirror, [contenteditable="true"]').last();
await body.click();
const missing = [];
for (const blk of blocks) {
  if (blk.kind === 'image') {
    // 画像は、ファイル選択の入力に直接渡す。見つからなければ手で入れる一覧に回す
    const input = p.locator('input[type="file"]').first();
    try {
      await input.setInputFiles(blk.file, { timeout: 4000 });
      await p.waitForTimeout(2500);
      await p.keyboard.press('End'); await p.keyboard.press('Enter');
    } catch (e) { missing.push(blk.file); }
    continue;
  }
  if (blk.kind === 'rule') { await p.keyboard.type('---'); await p.keyboard.press('Enter'); continue; }
  const prefix = blk.kind === 'h2' ? '## ' : blk.kind === 'h3' ? '### ' : blk.kind === 'quote' ? '> ' : '';
  // 太字（**）は、エディタ側の記法に任せず素の文字で入れる。崩れるより、あとで手で太くするほうが確実
  await p.keyboard.type(prefix + blk.text.replace(/\*\*/g, ''), { delay: 2 });
  await p.keyboard.press('Enter');
  if (blk.kind !== 'p') await p.keyboard.press('Enter');
}

// 下書き保存。公開ボタンは押さない
const save = p.getByRole('button', { name: /下書き保存|保存/ }).first();
try { await save.click({ timeout: 5000 }); await p.waitForTimeout(2500); console.log('下書きとして保存しました:', p.url()); }
catch (e) { console.log('保存ボタンが見つかりませんでした。ブラウザ上で手で保存してください（HEADED=1 で画面を出せます）'); }
if (missing.length) console.log('手で入れる画像:\n  ' + missing.join('\n  '));
if (!process.env.HEADED) await b.close();
