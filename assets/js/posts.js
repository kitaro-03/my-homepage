/* ==========================================================================
   トップページの「最近書いたもの」

   記事の本文は blog/posts/<slug>/ に静的HTMLとして出力済みで、
   ここで読むのはトップに出す「リンク一覧」だけ。
   一覧が数行なので、index.html を手書きのまま保つことを優先して実行時に読み込む。
   data/posts.json は tools/build_blog.py が生成する。
   ========================================================================== */
(() => {
  'use strict';

  const list   = document.getElementById('posts-list');
  const status = document.getElementById('posts-status');
  if (!list) return;

  function message(text) {
    list.textContent = '';
    if (!status) return;
    status.textContent = text;
    status.hidden = false;
  }

  fetch('data/posts.json', { cache: 'no-cache' })
    .then((res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then((data) => {
      const posts = (data && data.posts) || [];
      if (!posts.length) {
        message('まだ記事がありません。');
        return;
      }
      const frag = document.createDocumentFragment();
      posts.forEach((post) => {
        const time = document.createElement('time');
        time.dateTime = post.date || '';
        time.textContent = post.date || '';

        const title = document.createElement('span');
        title.className = 'post-list__title';
        title.textContent = post.title || '(無題)';

        const link = document.createElement('a');
        link.href = post.url || 'blog/';
        link.append(time, title);

        const item = document.createElement('li');
        item.appendChild(link);
        frag.appendChild(item);
      });
      list.appendChild(frag);
      if (status) status.hidden = true;
    })
    .catch((err) => {
      console.error('[posts]', err);
      // data/posts.json はビルドで生成されるので、未ビルドだとここに来る
      message('記事一覧を読み込めませんでした。python3 tools/build_blog.py を実行してください。');
    });
})();
