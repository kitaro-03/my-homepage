/* ==========================================================================
   制作物一覧の操作

   カードのHTMLそのものは data/works.json からビルド時に生成済み
   （tools/build_works.py）。このファイルがやるのは次の2つだけ:

     1. 種別による絞り込み（生成済みのカードを出し入れするだけ）
     2. 「ここで遊ぶ」でページ内ダイアログを開く

   JavaScript が動かなくても、カードは表示され、「ここで遊ぶ」は
   ゲームのページへの普通のリンクとして機能する。
   ========================================================================== */
(() => {
  'use strict';

  const grid      = document.getElementById('works-grid');
  const filterBox = document.getElementById('works-filter');
  const countBox  = document.getElementById('works-count');
  const statusBox = document.getElementById('works-status');
  if (!grid) return;

  const cards = Array.from(grid.querySelectorAll('.work-card'));

  /* ------------------------------------------------------------------
     絞り込み
     ------------------------------------------------------------------ */
  function applyFilter(type) {
    let shown = 0;
    cards.forEach((card) => {
      const match = (type === 'all') || (card.dataset.type === type);
      card.hidden = !match;
      if (match) shown++;
    });

    if (countBox) countBox.textContent = `${shown} 件`;
    if (statusBox) {
      statusBox.textContent = shown ? '' : '該当する制作物はまだありません。';
      statusBox.hidden = shown > 0;
    }
  }

  if (filterBox) {
    filterBox.addEventListener('click', (e) => {
      const btn = e.target.closest('button[data-filter]');
      if (!btn) return;
      filterBox.querySelectorAll('button[data-filter]').forEach((b) => {
        b.setAttribute('aria-pressed', String(b === btn));
      });
      applyFilter(btn.dataset.filter);
    });
  }

  /* ------------------------------------------------------------------
     ゲーム埋め込みダイアログ
     ★ この中には広告を置かない（操作エリアと広告を分離する方針）
     ------------------------------------------------------------------ */
  const dialog      = document.getElementById('game-dialog');
  const dialogTitle = document.getElementById('game-dialog-title');
  const dialogStage = document.getElementById('game-dialog-stage');
  const dialogHint  = document.getElementById('game-dialog-hint');
  const dialogOpen  = document.getElementById('game-dialog-open');

  function openGame(card) {
    const src      = card.dataset.embedSrc;
    const aspect   = card.dataset.embedAspect || '16 / 9';
    const controls = card.dataset.embedControls || '';
    const title    = card.dataset.title || '';

    // 比率から「高さの上限に収まる幅」を求める。CSS側の max-width に渡す。
    const [aw, ah] = aspect.split('/').map((n) => parseFloat(n));
    const ratio = (aw > 0 && ah > 0) ? aw / ah : 16 / 9;

    dialogTitle.textContent = title;
    dialogHint.textContent  = controls;
    dialogOpen.href         = src;
    dialogStage.style.setProperty('--embed-aspect', aspect);
    dialogStage.style.setProperty('--embed-max-width', `calc((92vh - 132px) * ${ratio})`);

    // iframe は開くたびに作り直す（閉じたときに確実に停止させるため）
    dialogStage.textContent = '';
    const frame = document.createElement('iframe');
    frame.src = src;
    frame.title = `${title} のプレイ画面`;
    frame.setAttribute('allow', 'autoplay; fullscreen; gamepad');
    frame.setAttribute('allowfullscreen', '');
    dialogStage.appendChild(frame);

    dialog.showModal();
  }

  if (dialog && typeof dialog.showModal === 'function') {
    // 「ここで遊ぶ」は素のリンク。JSが動くときだけ横取りしてダイアログで開く。
    grid.addEventListener('click', (e) => {
      const trigger = e.target.closest('[data-play]');
      if (!trigger) return;
      const card = trigger.closest('.work-card');
      if (!card || !card.dataset.embedSrc) return;
      e.preventDefault();
      openGame(card);
    });

    // 閉じたら iframe を破棄 = ゲームのループも音も止まる
    dialog.addEventListener('close', () => { dialogStage.textContent = ''; });
    dialog.addEventListener('click', (e) => {
      if (e.target === dialog) dialog.close();   // 背景クリックで閉じる
    });
    document.getElementById('game-dialog-close')
      ?.addEventListener('click', () => dialog.close());
  }
})();
