/* ==========================================================================
   制作物一覧の描画
   data/works.json を読み込んで、カードのDOMを組み立てる。
   HTML側には空の <ul id="works-grid"> があるだけで、中身は全部ここで作る。
   ========================================================================== */
(() => {
  'use strict';

  const DATA_URL = 'data/works.json';

  const grid      = document.getElementById('works-grid');
  const statusBox = document.getElementById('works-status');
  const filterBox = document.getElementById('works-filter');
  const countBox  = document.getElementById('works-count');
  if (!grid) return;

  /** 現在のフィルタ: 'all' | 'embed' | 'link' */
  let currentFilter = 'all';
  /** 読み込んだ制作物データ */
  let works = [];

  /* ------------------------------------------------------------------
     小さなヘルパー
     ------------------------------------------------------------------ */

  /** タグ名・属性・子要素から要素を作る */
  function el(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
      if (value === null || value === undefined || value === false) continue;
      if (key === 'class') node.className = value;
      else if (key === 'text') node.textContent = value;
      else if (key === 'html') node.innerHTML = value;
      else node.setAttribute(key, value);
    }
    for (const child of [].concat(children)) {
      if (child) node.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
    }
    return node;
  }

  /**
   * 外部サイトかどうか。
   * 外部リンクには target="_blank" と rel="noopener" を付ける。
   */
  function isExternal(url) {
    return /^https?:\/\//i.test(url);
  }

  /**
   * サムネ画像がないときの背景色を、idの文字列から決める。
   * 同じ作品は常に同じ色になるので、見た目が毎回変わらない。
   */
  function autoColor(seed) {
    let hash = 0;
    for (let i = 0; i < seed.length; i++) hash = (hash * 31 + seed.charCodeAt(i)) % 360;
    return `linear-gradient(135deg, hsl(${hash} 62% 42%), hsl(${(hash + 48) % 360} 58% 30%))`;
  }

  /**
   * プレースホルダに出す頭文字。
   * 「（サンプル）〜」のような括弧や記号で始まるタイトルでも、
   * 意味のある最初の1文字を拾えるようにする。
   */
  function initial(title) {
    const match = String(title || '').match(/[\p{L}\p{N}]/u);
    return match ? match[0] : '?';
  }

  /** links の kind に応じたラベル用の記号 */
  const KIND_MARK = {
    github: '{ }',
    itch: '▶',
    googleplay: '▶',
    appstore: '',
    blog: '✎',
    site: '↗',
  };

  /* ------------------------------------------------------------------
     カード1枚を組み立てる
     ------------------------------------------------------------------ */
  function buildCard(work) {
    const isEmbed = work.type === 'embed' && work.embed && work.embed.src;

    /* --- サムネイル --- */
    const badges = el('div', { class: 'work-card__badges' });
    badges.appendChild(el('span', {
      class: `badge ${isEmbed ? 'badge--playable' : 'badge--link'}`,
      text: isEmbed ? 'ブラウザで遊べる' : '外部リンク',
    }));
    if (work.status === 'wip')    badges.appendChild(el('span', { class: 'badge badge--wip', text: '制作中' }));
    if (work.status === 'sample') badges.appendChild(el('span', { class: 'badge badge--sample', text: 'サンプル' }));

    let thumb;
    if (work.thumbnail) {
      thumb = el('div', { class: 'work-card__thumb' }, [
        el('img', { src: work.thumbnail, alt: '', loading: 'lazy', decoding: 'async' }),
      ]);
    } else {
      // 画像がない場合はタイトル頭文字のプレースホルダを生成する
      thumb = el('div', {
        class: 'work-card__thumb work-card__thumb--auto',
        style: `background: ${autoColor(work.id || work.title)}`,
        text: initial(work.title),
        'aria-hidden': 'true',
      });
    }
    thumb.appendChild(badges);

    /* --- 本文 --- */
    const metaParts = [];
    if (work.year) metaParts.push(work.year);
    if (Array.isArray(work.tags) && work.tags.length) metaParts.push(`${work.tags.length} tags`);

    const body = el('div', { class: 'work-card__body' }, [
      el('h3', { class: 'work-card__title', text: work.title || '(無題)' }),
      work.year ? el('p', { class: 'work-card__meta', text: work.year }) : null,
      el('p', { class: 'work-card__summary', text: work.summary || '' }),
    ]);

    if (Array.isArray(work.tags) && work.tags.length) {
      body.appendChild(el('ul', { class: 'tag-list' },
        work.tags.map((t) => el('li', { text: t }))));
    }

    /* --- ボタン類 --- */
    const actions = el('div', { class: 'work-card__actions' });

    if (isEmbed) {
      // ページ内で遊ぶボタン（ダイアログを開く）
      const playBtn = el('button', {
        type: 'button',
        class: 'btn btn--primary btn--sm',
        'data-play': work.id,
        text: '▶ ここで遊ぶ',
      });
      actions.appendChild(playBtn);
    }

    const links = Array.isArray(work.links) ? work.links : [];
    // link 種別は primary リンクを主ボタンにする
    links.forEach((link) => {
      if (!link || !link.url) return;
      const primary = !isEmbed && link.primary;
      const mark = KIND_MARK[link.kind] || '↗';
      actions.appendChild(el('a', {
        class: `btn btn--sm ${primary ? 'btn--primary' : 'btn--ghost'}`,
        href: link.url,
        target: isExternal(link.url) ? '_blank' : null,
        rel: isExternal(link.url) ? 'noopener noreferrer' : null,
        text: `${mark} ${link.label || 'リンク'}`,
      }));
    });

    if (!actions.childElementCount) {
      actions.appendChild(el('span', { class: 'work-card__meta', text: '準備中' }));
    }
    body.appendChild(actions);

    return el('li', {
      class: 'work-card',
      id: `work-${work.id}`,
      'data-type': isEmbed ? 'embed' : 'link',
    }, [thumb, body]);
  }

  /* ------------------------------------------------------------------
     一覧の描画
     ------------------------------------------------------------------ */
  function render() {
    const list = works.filter((w) => {
      if (currentFilter === 'all') return true;
      const type = (w.type === 'embed' && w.embed && w.embed.src) ? 'embed' : 'link';
      return type === currentFilter;
    });

    grid.textContent = '';
    if (!list.length) {
      statusBox.className = 'works-status';
      statusBox.textContent = '該当する制作物はまだありません。';
      statusBox.hidden = false;
      return;
    }
    statusBox.hidden = true;

    const frag = document.createDocumentFragment();
    list.forEach((w) => frag.appendChild(buildCard(w)));
    grid.appendChild(frag);

    if (countBox) {
      countBox.textContent = `${list.length} 件`;
    }
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

  function openGame(work) {
    if (!dialog || !dialogStage) {
      window.open(work.embed.src, '_blank', 'noopener');
      return;
    }
    const aspect = work.embed.aspect || '16 / 9';
    // 比率から「高さの上限に収まる幅」を求める。CSS側の max-width に渡す。
    const [aw, ah] = aspect.split('/').map((n) => parseFloat(n));
    const ratio = (aw > 0 && ah > 0) ? aw / ah : 16 / 9;

    dialogTitle.textContent = work.title;
    dialogHint.textContent  = work.embed.controls || '';
    dialogOpen.href         = work.embed.src;
    dialogStage.style.setProperty('--embed-aspect', aspect);
    dialogStage.style.setProperty('--embed-max-width', `calc((92vh - 132px) * ${ratio})`);

    // iframe は開くたびに作り直す（閉じたときに確実に停止させるため）
    dialogStage.textContent = '';
    dialogStage.appendChild(el('iframe', {
      src: work.embed.src,
      title: `${work.title} のプレイ画面`,
      allow: 'autoplay; fullscreen; gamepad',
      allowfullscreen: '',
      loading: 'lazy',
    }));

    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open', '');
  }

  function closeGame() {
    // iframeを破棄 = ゲームのループも音も止まる
    if (dialogStage) dialogStage.textContent = '';
  }

  if (dialog) {
    dialog.addEventListener('close', closeGame);
    dialog.addEventListener('click', (e) => {
      // 背景（ダイアログ自身）のクリックで閉じる
      if (e.target === dialog) dialog.close();
    });
    document.getElementById('game-dialog-close')?.addEventListener('click', () => dialog.close());
  }

  // カード内の「ここで遊ぶ」ボタン（動的生成なので親でまとめて受ける）
  grid.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-play]');
    if (!btn) return;
    const work = works.find((w) => w.id === btn.dataset.play);
    if (work) openGame(work);
  });

  /* ------------------------------------------------------------------
     フィルタボタン
     ------------------------------------------------------------------ */
  if (filterBox) {
    filterBox.addEventListener('click', (e) => {
      const btn = e.target.closest('button[data-filter]');
      if (!btn) return;
      currentFilter = btn.dataset.filter;
      filterBox.querySelectorAll('button[data-filter]').forEach((b) => {
        b.setAttribute('aria-pressed', String(b === btn));
      });
      render();
    });
  }

  /* ------------------------------------------------------------------
     データの読み込み
     ------------------------------------------------------------------ */
  function showError(message, detail) {
    grid.textContent = '';
    statusBox.className = 'works-status works-status--error';
    statusBox.textContent = message;
    statusBox.hidden = false;
    if (detail) console.error('[works]', detail);
  }

  fetch(DATA_URL, { cache: 'no-cache' })
    .then((res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then((data) => {
      works = Array.isArray(data) ? data : (data.works || []);
      render();
    })
    .catch((err) => {
      if (location.protocol === 'file:') {
        showError('ローカルのファイルを直接開くと、制作物リスト（JSON）を読み込めません。'
          + ' ターミナルで python3 -m http.server を実行して http://localhost:8000 から開いてください。', err);
      } else {
        showError('制作物リストを読み込めませんでした。data/works.json の書式を確認してください。', err);
      }
    });
})();
