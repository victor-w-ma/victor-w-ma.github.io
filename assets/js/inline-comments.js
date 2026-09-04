(function () {
  var CONTEXT_LEN = 32;
  var MIN_QUOTE_CHARS = 2;
  var MAX_QUOTE_CHARS = 800;
  var MIN_GUTTER = 240;
  var NICK_KEY = 'inline_comment_nickname';

  var postId = window.INLINE_COMMENTS_POST_ID;
  if (!postId) {
    return;
  }

  var toolbar = document.getElementById('inline-comment-toolbar');
  var addBtn = document.getElementById('inline-comment-add-btn');
  var panel = document.getElementById('inline-comment-panel');
  var backdrop = document.getElementById('inline-comment-backdrop');
  if (!toolbar || !addBtn || !panel || !backdrop) {
    return;
  }

  var quoteEl = panel.querySelector('.inline-comment-quote');
  var threadEl = panel.querySelector('.inline-comment-thread');
  var form = panel.querySelector('.inline-comment-form');
  var nickInput = form.querySelector('input[name="nickname"]');
  var commentInput = form.querySelector('textarea[name="comment"]');
  var submitBtn = form.querySelector('button[type="submit"]');
  var errorEl = panel.querySelector('.inline-comment-error');
  var titleEl = document.getElementById('inline-comment-panel-title');
  var closeBtn = panel.querySelector('.inline-comment-close');

  var threads = {};
  var currentThreadId = null;
  var pendingAnchor = null;
  var lastAnchorRect = null;
  var toolbarTimer = null;
  var openReply = null;
  var database = null;

  function contentRoot() {
    return document.querySelector('.post-content');
  }

  function articleRoot() {
    return document.querySelector('article.post');
  }

  function escapeAttr(value) {
    return String(value).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
  }

  function savedNickname() {
    var bottom = document.getElementById('nickname');
    if (bottom && bottom.value) {
      return bottom.value;
    }
    try {
      return localStorage.getItem(NICK_KEY) || '';
    } catch (err) {
      return '';
    }
  }

  function rememberNickname(name) {
    try {
      localStorage.setItem(NICK_KEY, name);
    } catch (err) {
      /* ignore quota / private mode */
    }
    var bottom = document.getElementById('nickname');
    if (bottom && !bottom.value) {
      bottom.value = name;
    }
  }

  function formatTime(ts) {
    if (!ts) {
      return '';
    }
    var d = new Date(ts);
    if (isNaN(d.getTime())) {
      return '';
    }
    function pad(n) {
      return (n < 10 ? '0' : '') + n;
    }
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) +
        ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
  }

  function displayQuote(quote) {
    var text = String(quote || '').replace(/\s+/g, ' ').trim();
    if (text.length > 80) {
      return text.slice(0, 80) + '…';
    }
    return text;
  }

  function countComments(thread) {
    if (!thread || !thread.comments) {
      return 0;
    }
    return Object.keys(thread.comments).length;
  }

  function skipNode(node) {
    var parent = node.parentElement;
    if (!parent) {
      return true;
    }
    if (parent.closest('script, style, noscript, #toc, .inline-comment-toolbar, .inline-comment-panel, .inline-comment-backdrop')) {
      return true;
    }
    if (parent.tagName === 'H1' && parent.textContent === '目录') {
      return true;
    }
    return false;
  }

  function collectTextNodes(root) {
    var nodes = [];
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (!node.nodeValue) {
          return NodeFilter.FILTER_REJECT;
        }
        if (skipNode(node)) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var current = walker.nextNode();
    while (current) {
      nodes.push(current);
      current = walker.nextNode();
    }
    return nodes;
  }

  function buildIndex(nodes) {
    var text = '';
    var spans = [];
    var i;
    for (i = 0; i < nodes.length; i++) {
      var start = text.length;
      text += nodes[i].nodeValue;
      spans.push({
        node: nodes[i],
        start: start,
        end: text.length
      });
    }
    return { text: text, spans: spans };
  }

  function commonSuffixLen(a, b) {
    var i = 0;
    var max = Math.min(a.length, b.length);
    while (i < max && a.charAt(a.length - 1 - i) === b.charAt(b.length - 1 - i)) {
      i++;
    }
    return i;
  }

  function commonPrefixLen(a, b) {
    var i = 0;
    var max = Math.min(a.length, b.length);
    while (i < max && a.charAt(i) === b.charAt(i)) {
      i++;
    }
    return i;
  }

  function scoreHit(text, index, quote, prefix, suffix) {
    var pre = text.slice(Math.max(0, index - prefix.length), index);
    var suf = text.slice(index + quote.length, index + quote.length + suffix.length);
    var score = 0;
    if (prefix && pre === prefix) {
      score += 10;
    } else if (prefix && (pre.endsWith(prefix) || prefix.endsWith(pre))) {
      score += 5;
    }
    if (suffix && suf === suffix) {
      score += 10;
    } else if (suffix && (suf.startsWith(suffix) || suffix.startsWith(suf))) {
      score += 5;
    }
    score += commonSuffixLen(pre, prefix);
    score += commonPrefixLen(suf, suffix);
    return score;
  }

  function findQuote(text, quote, prefix, suffix) {
    if (!quote) {
      return null;
    }
    var hits = [];
    var from = 0;
    var index = text.indexOf(quote, from);
    while (index !== -1) {
      hits.push(index);
      from = index + 1;
      index = text.indexOf(quote, from);
    }
    if (!hits.length) {
      return null;
    }
    var best = hits[0];
    var bestScore = -1;
    var i;
    for (i = 0; i < hits.length; i++) {
      var score = scoreHit(text, hits[i], quote, prefix || '', suffix || '');
      if (score > bestScore) {
        bestScore = score;
        best = hits[i];
      }
    }
    return { start: best, end: best + quote.length };
  }

  function rangeToOffsets(range, spans) {
    var start = null;
    var end = null;
    var i;
    for (i = 0; i < spans.length; i++) {
      if (spans[i].node === range.startContainer) {
        start = spans[i].start + range.startOffset;
      }
      if (spans[i].node === range.endContainer) {
        end = spans[i].start + range.endOffset;
      }
    }
    return { start: start, end: end };
  }

  function unwrapMarks(root) {
    var marks = root.querySelectorAll('mark.inline-comment-mark');
    var i;
    for (i = 0; i < marks.length; i++) {
      var mark = marks[i];
      var parent = mark.parentNode;
      if (!parent) {
        continue;
      }
      while (mark.firstChild) {
        parent.insertBefore(mark.firstChild, mark);
      }
      parent.removeChild(mark);
      parent.normalize();
    }
  }

  function wrapPortion(node, startOffset, endOffset, threadId) {
    if (!node || !node.nodeValue) {
      return;
    }
    var text = node.nodeValue;
    if (startOffset < 0) {
      startOffset = 0;
    }
    if (endOffset > text.length) {
      endOffset = text.length;
    }
    if (startOffset >= endOffset) {
      return;
    }
    var parent = node.parentNode;
    if (!parent) {
      return;
    }
    if (parent.classList && parent.classList.contains('inline-comment-mark') &&
        parent.getAttribute('data-thread-id') === threadId &&
        startOffset === 0 && endOffset === text.length) {
      return;
    }
    var mark = document.createElement('mark');
    mark.className = 'inline-comment-mark';
    mark.setAttribute('data-thread-id', threadId);
    mark.setAttribute('role', 'button');
    mark.tabIndex = 0;
    mark.textContent = text.slice(startOffset, endOffset);
    if (startOffset > 0) {
      parent.insertBefore(document.createTextNode(text.slice(0, startOffset)), node);
    }
    parent.insertBefore(mark, node);
    if (endOffset < text.length) {
      parent.insertBefore(document.createTextNode(text.slice(endOffset)), node);
    }
    parent.removeChild(node);
  }

  function wrapQuote(root, thread, threadId) {
    var nodes = collectTextNodes(root);
    var index = buildIndex(nodes);
    var found = findQuote(index.text, thread.quote, thread.prefix || '', thread.suffix || '');
    if (!found) {
      return false;
    }
    var portions = [];
    var i;
    for (i = 0; i < index.spans.length; i++) {
      var span = index.spans[i];
      var start = Math.max(span.start, found.start);
      var end = Math.min(span.end, found.end);
      if (start < end) {
        portions.push({
          node: span.node,
          startOffset: start - span.start,
          endOffset: end - span.start
        });
      }
    }
    for (i = portions.length - 1; i >= 0; i--) {
      wrapPortion(portions[i].node, portions[i].startOffset, portions[i].endOffset, threadId);
    }
    return portions.length > 0;
  }

  function updateMarkLabels() {
    var root = contentRoot();
    if (!root) {
      return;
    }
    var marks = root.querySelectorAll('mark.inline-comment-mark');
    var i;
    for (i = 0; i < marks.length; i++) {
      var id = marks[i].getAttribute('data-thread-id');
      var n = countComments(threads[id]);
      var label = n > 0 ? '查看这段的 ' + n + ' 条评论' : '查看这段的评论';
      marks[i].setAttribute('aria-label', label);
      marks[i].title = label;
    }
  }

  function refreshHighlights() {
    var root = contentRoot();
    if (!root) {
      return;
    }
    unwrapMarks(root);
    var ids = Object.keys(threads);
    ids.sort(function (a, b) {
      return String(threads[b].quote || '').length - String(threads[a].quote || '').length;
    });
    var i;
    for (i = 0; i < ids.length; i++) {
      wrapQuote(root, threads[ids[i]], ids[i]);
    }
    if (currentThreadId) {
      var active = root.querySelectorAll(
          'mark.inline-comment-mark[data-thread-id="' + escapeAttr(currentThreadId) + '"]');
      for (i = 0; i < active.length; i++) {
        active[i].classList.add('is-active');
      }
    }
    updateMarkLabels();
  }

  function availableRightGutter() {
    var content = contentRoot();
    if (!content) {
      return 0;
    }
    return window.innerWidth - content.getBoundingClientRect().right - 16;
  }

  function isWideLayout() {
    return availableRightGutter() >= MIN_GUTTER;
  }

  function hideToolbar() {
    toolbar.hidden = true;
  }

  function selectionRange() {
    var sel = window.getSelection();
    if (!sel || sel.rangeCount === 0 || sel.isCollapsed) {
      return null;
    }
    return sel.getRangeAt(0);
  }

  function isUsableRange(range) {
    var root = contentRoot();
    if (!root || !range) {
      return false;
    }
    var start = range.startContainer;
    var end = range.endContainer;
    if (!root.contains(start) || !root.contains(end)) {
      return false;
    }
    if (start.parentElement && start.parentElement.closest(
        'input, textarea, .inline-comment-panel, .inline-comment-toolbar, #toc')) {
      return false;
    }
    return true;
  }

  function captureAnchor(range) {
    var root = contentRoot();
    var nodes = collectTextNodes(root);
    var index = buildIndex(nodes);
    var offsets = rangeToOffsets(range, index.spans);
    var quote;
    var start;
    var end;
    if (offsets.start !== null && offsets.end !== null && offsets.end > offsets.start) {
      start = offsets.start;
      end = offsets.end;
      quote = index.text.slice(start, end);
    } else {
      quote = range.toString();
      start = index.text.indexOf(quote);
      end = start === -1 ? -1 : start + quote.length;
    }
    if (!quote || quote.replace(/\s+/g, '').length < MIN_QUOTE_CHARS) {
      return null;
    }
    if (quote.length > MAX_QUOTE_CHARS) {
      return null;
    }
    var prefix = '';
    var suffix = '';
    if (start >= 0) {
      prefix = index.text.slice(Math.max(0, start - CONTEXT_LEN), start);
      suffix = index.text.slice(end, end + CONTEXT_LEN);
    }
    var rects = range.getClientRects();
    var rect = rects.length ? rects[rects.length - 1] : range.getBoundingClientRect();
    return {
      quote: quote,
      prefix: prefix,
      suffix: suffix,
      clientRect: rect ? { top: rect.top, bottom: rect.bottom, left: rect.left, right: rect.right, width: rect.width, height: rect.height } : null
    };
  }

  function findExistingThreadId(anchor) {
    var id;
    var bestId = null;
    var bestScore = -1;
    for (id in threads) {
      if (!Object.prototype.hasOwnProperty.call(threads, id)) {
        continue;
      }
      var thread = threads[id];
      if (thread.quote !== anchor.quote) {
        continue;
      }
      var score = 0;
      if ((thread.prefix || '') === (anchor.prefix || '')) {
        score += 2;
      }
      if ((thread.suffix || '') === (anchor.suffix || '')) {
        score += 2;
      }
      if (score > bestScore) {
        bestScore = score;
        bestId = id;
      }
    }
    return bestId;
  }

  function placeToolbarForRange(range) {
    var rects = range.getClientRects();
    var rect = rects.length ? rects[rects.length - 1] : range.getBoundingClientRect();
    if (!rect || (rect.width === 0 && rect.height === 0)) {
      hideToolbar();
      return;
    }
    toolbar.hidden = false;
    var top = rect.top - 8;
    var left = rect.left + rect.width / 2;
    toolbar.style.transform = 'translate(-50%, -100%)';
    if (top < 44) {
      top = rect.bottom + 8;
      toolbar.style.transform = 'translate(-50%, 0)';
    }
    var toolbarWidth = toolbar.offsetWidth || 88;
    left = Math.min(window.innerWidth - toolbarWidth / 2 - 8, Math.max(toolbarWidth / 2 + 8, left));
    toolbar.style.left = left + 'px';
    toolbar.style.top = top + 'px';
  }

  function updateToolbar() {
    var range = selectionRange();
    if (!isUsableRange(range) || panel.contains(document.activeElement)) {
      hideToolbar();
      return;
    }
    var anchor = captureAnchor(range);
    if (!anchor) {
      hideToolbar();
      return;
    }
    pendingAnchor = anchor;
    lastAnchorRect = anchor.clientRect;
    placeToolbarForRange(range);
  }

  function scheduleToolbar() {
    window.clearTimeout(toolbarTimer);
    toolbarTimer = window.setTimeout(updateToolbar, 80);
  }

  function placeOverlay(anchorRect) {
    var panelWidth = Math.min(360, window.innerWidth - 24);
    var padding = 12;
    panel.style.position = 'fixed';
    panel.style.width = panelWidth + 'px';
    panel.style.right = 'auto';
    panel.style.left = '0px';
    panel.style.top = '0px';
    var height = panel.offsetHeight;
    var spaceBelow = window.innerHeight - anchorRect.bottom;
    var spaceAbove = anchorRect.top;
    var top;
    if (spaceBelow >= height + padding || spaceBelow >= spaceAbove) {
      top = anchorRect.bottom + 8;
      if (top + height > window.innerHeight - padding) {
        top = Math.max(padding, window.innerHeight - height - padding);
      }
    } else {
      top = anchorRect.top - height - 8;
      if (top < padding) {
        top = padding;
      }
    }
    var left = anchorRect.left + (anchorRect.width / 2) - (panelWidth / 2);
    left = Math.min(window.innerWidth - panelWidth - 12, Math.max(12, left));
    panel.style.left = left + 'px';
    panel.style.top = top + 'px';
  }

  function positionPanel() {
    var article = articleRoot();
    var content = contentRoot();
    if (!article || !content) {
      return;
    }
    var anchorRect = lastAnchorRect;
    if (currentThreadId) {
      var mark = content.querySelector(
          'mark.inline-comment-mark[data-thread-id="' + escapeAttr(currentThreadId) + '"]');
      if (mark) {
        var markRect = mark.getBoundingClientRect();
        anchorRect = {
          top: markRect.top,
          bottom: markRect.bottom,
          left: markRect.left,
          right: markRect.right,
          width: markRect.width,
          height: markRect.height
        };
        lastAnchorRect = anchorRect;
      }
    }
    if (!anchorRect) {
      return;
    }
    if (isWideLayout()) {
      backdrop.hidden = true;
      panel.classList.add('is-wide');
      panel.classList.remove('is-overlay');
      panel.setAttribute('aria-modal', 'false');
      var articleRect = article.getBoundingClientRect();
      panel.style.position = 'absolute';
      panel.style.left = 'calc(100% + 12px)';
      panel.style.right = 'auto';
      panel.style.top = Math.max(0, anchorRect.top - articleRect.top) + 'px';
      panel.style.width = Math.min(320, Math.max(240, availableRightGutter() - 8)) + 'px';
    } else {
      panel.classList.remove('is-wide');
      panel.classList.add('is-overlay');
      panel.setAttribute('aria-modal', 'true');
      backdrop.hidden = false;
      placeOverlay(anchorRect);
    }
  }

  function showError(message) {
    if (!message) {
      errorEl.hidden = true;
      errorEl.textContent = '';
      return;
    }
    errorEl.hidden = false;
    errorEl.textContent = message;
  }

  function closePanel() {
    currentThreadId = null;
    pendingAnchor = null;
    openReply = null;
    panel.hidden = true;
    backdrop.hidden = true;
    panel.classList.remove('is-wide', 'is-overlay');
    showError('');
    var root = contentRoot();
    if (root) {
      var active = root.querySelectorAll('mark.inline-comment-mark.is-active');
      var i;
      for (i = 0; i < active.length; i++) {
        active[i].classList.remove('is-active');
      }
    }
  }

  function renderCommentItem(item) {
    var wrap = document.createElement('div');
    wrap.className = 'inline-comment-item';
    wrap.setAttribute('data-comment-id', item.id);

    var meta = document.createElement('div');
    meta.className = 'inline-comment-meta';
    var author = document.createElement('span');
    author.className = 'inline-comment-author';
    author.textContent = item.nickname || '匿名';
    var time = document.createElement('span');
    time.className = 'inline-comment-time';
    time.textContent = formatTime(item.timestamp);
    meta.appendChild(author);
    if (time.textContent) {
      meta.appendChild(time);
    }

    var body = document.createElement('div');
    body.className = 'inline-comment-body';
    body.textContent = item.comment || '';

    var actions = document.createElement('div');
    actions.className = 'inline-comment-item-actions';
    var replyBtn = document.createElement('button');
    replyBtn.type = 'button';
    replyBtn.className = 'inline-comment-reply-btn';
    replyBtn.textContent = '回复';
    replyBtn.addEventListener('click', function () {
      showReplyForm(wrap, item.id);
    });
    actions.appendChild(replyBtn);

    wrap.appendChild(meta);
    wrap.appendChild(body);
    wrap.appendChild(actions);
    return wrap;
  }

  function showReplyForm(itemEl, parentId) {
    var existing = threadEl.querySelector('.inline-comment-reply-form');
    if (existing) {
      existing.remove();
    }
    if (openReply && openReply.parentId === parentId) {
      openReply = null;
      return;
    }
    var replyForm = document.createElement('form');
    replyForm.className = 'inline-comment-reply-form';
    var replyNick = document.createElement('input');
    replyNick.type = 'text';
    replyNick.name = 'nickname';
    replyNick.placeholder = '昵称';
    replyNick.required = true;
    replyNick.value = savedNickname();
    var replyText = document.createElement('textarea');
    replyText.name = 'comment';
    replyText.placeholder = '回复';
    replyText.required = true;
    var replyActions = document.createElement('div');
    replyActions.className = 'inline-comment-form-actions';
    var replySubmit = document.createElement('button');
    replySubmit.type = 'submit';
    replySubmit.textContent = '发布';
    replyActions.appendChild(replySubmit);
    replyForm.appendChild(replyNick);
    replyForm.appendChild(replyText);
    replyForm.appendChild(replyActions);
    itemEl.appendChild(replyForm);
    openReply = { parentId: parentId, form: replyForm };
    replyText.focus();
    replyForm.addEventListener('submit', function (event) {
      event.preventDefault();
      if (!currentThreadId) {
        return;
      }
      var nickname = replyNick.value.trim();
      var comment = replyText.value.trim();
      if (!nickname || !comment) {
        return;
      }
      rememberNickname(nickname);
      addComment(currentThreadId, nickname, comment, parentId);
    });
    positionPanel();
  }

  function renderThread() {
    var savedReplyParent = openReply ? openReply.parentId : null;
    var savedReplyNick = '';
    var savedReplyText = '';
    if (openReply && openReply.form) {
      savedReplyNick = openReply.form.querySelector('input').value;
      savedReplyText = openReply.form.querySelector('textarea').value;
    }
    threadEl.textContent = '';
    openReply = null;
    if (!currentThreadId || !threads[currentThreadId]) {
      return;
    }
    var commentsMap = threads[currentThreadId].comments || {};
    var items = [];
    var id;
    for (id in commentsMap) {
      if (Object.prototype.hasOwnProperty.call(commentsMap, id)) {
        var row = commentsMap[id];
        items.push({
          id: id,
          nickname: row.nickname,
          comment: row.comment,
          timestamp: row.timestamp,
          parentId: row.parentId || ''
        });
      }
    }
    items.sort(function (a, b) {
      return (a.timestamp || 0) - (b.timestamp || 0);
    });
    var byParent = {};
    var i;
    for (i = 0; i < items.length; i++) {
      var key = items[i].parentId || '';
      if (!byParent[key]) {
        byParent[key] = [];
      }
      byParent[key].push(items[i]);
    }

    function renderList(parentKey, mount) {
      var list = byParent[parentKey] || [];
      var j;
      for (j = 0; j < list.length; j++) {
        var node = renderCommentItem(list[j]);
        mount.appendChild(node);
        if (byParent[list[j].id] && byParent[list[j].id].length) {
          var nested = document.createElement('div');
          nested.className = 'inline-comment-replies';
          node.appendChild(nested);
          renderList(list[j].id, nested);
        }
      }
    }

    renderList('', threadEl);
    if (savedReplyParent) {
      var parentItem = threadEl.querySelector(
          '.inline-comment-item[data-comment-id="' + escapeAttr(savedReplyParent) + '"]');
      if (parentItem) {
        showReplyForm(parentItem, savedReplyParent);
        if (openReply && openReply.form) {
          openReply.form.querySelector('input').value = savedReplyNick;
          openReply.form.querySelector('textarea').value = savedReplyText;
        }
      }
    }
  }

  function openPanel(threadId, anchor) {
    currentThreadId = threadId || null;
    pendingAnchor = threadId ? null : anchor;
    hideToolbar();
    var quote = '';
    if (threadId && threads[threadId]) {
      quote = threads[threadId].quote;
      titleEl.textContent = '这段话的评论';
    } else if (anchor) {
      quote = anchor.quote;
      titleEl.textContent = '评论这段话';
      lastAnchorRect = anchor.clientRect;
    }
    quoteEl.textContent = displayQuote(quote);
    quoteEl.hidden = !quote;
    if (!nickInput.value) {
      nickInput.value = savedNickname();
    }
    showError('');
    renderThread();
    panel.hidden = false;
    refreshHighlights();
    positionPanel();
    if (!threadId) {
      commentInput.focus();
    }
  }

  function openThread(threadId) {
    if (!threads[threadId]) {
      return;
    }
    if (currentThreadId === threadId && !panel.hidden) {
      closePanel();
      return;
    }
    openPanel(threadId, null);
  }

  function addComment(threadId, nickname, comment, parentId) {
    if (!database) {
      showError('评论服务还没准备好，请稍后再试。');
      return Promise.reject(new Error('no database'));
    }
    submitBtn.disabled = true;
    return database.ref('inlineComments/' + postId + '/' + threadId + '/comments').push({
      nickname: nickname,
      comment: comment,
      timestamp: firebase.database.ServerValue.TIMESTAMP,
      parentId: parentId || null
    }).then(function () {
      commentInput.value = '';
      submitBtn.disabled = false;
      showError('');
    }).catch(function (err) {
      submitBtn.disabled = false;
      showError('发布失败，请重试。');
      console.error('inline comment failed', err);
    });
  }

  function createThread(anchor, nickname, comment) {
    if (!database) {
      showError('评论服务还没准备好，请稍后再试。');
      return Promise.reject(new Error('no database'));
    }
    var threadRef = database.ref('inlineComments/' + postId).push();
    var commentRef = threadRef.child('comments').push();
    var payload = {
      quote: anchor.quote,
      prefix: anchor.prefix,
      suffix: anchor.suffix,
      createdAt: firebase.database.ServerValue.TIMESTAMP,
      comments: {}
    };
    payload.comments[commentRef.key] = {
      nickname: nickname,
      comment: comment,
      timestamp: firebase.database.ServerValue.TIMESTAMP,
      parentId: null
    };
    submitBtn.disabled = true;
    return threadRef.set(payload).then(function () {
      currentThreadId = threadRef.key;
      pendingAnchor = null;
      commentInput.value = '';
      submitBtn.disabled = false;
      titleEl.textContent = '这段话的评论';
      showError('');
    }).catch(function (err) {
      submitBtn.disabled = false;
      showError('发布失败，请重试。');
      console.error('inline thread failed', err);
    });
  }

  function onAddClick(event) {
    event.preventDefault();
    event.stopPropagation();
    var range = selectionRange();
    var anchor = pendingAnchor;
    if (isUsableRange(range)) {
      anchor = captureAnchor(range) || anchor;
    }
    if (!anchor) {
      hideToolbar();
      return;
    }
    var existingId = findExistingThreadId(anchor);
    if (existingId) {
      openPanel(existingId, null);
      return;
    }
    if (window.getSelection) {
      window.getSelection().removeAllRanges();
    }
    hideToolbar();
    openPanel(null, anchor);
  }

  function onContentClick(event) {
    var mark = event.target.closest ? event.target.closest('mark.inline-comment-mark') : null;
    if (!mark || !contentRoot().contains(mark)) {
      return;
    }
    event.preventDefault();
    openThread(mark.getAttribute('data-thread-id'));
  }

  function onContentKeydown(event) {
    var mark = event.target.closest ? event.target.closest('mark.inline-comment-mark') : null;
    if (!mark) {
      return;
    }
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      openThread(mark.getAttribute('data-thread-id'));
    }
  }

  function onDocumentPointerDown(event) {
    var target = event.target;
    if (toolbar.contains(target) || panel.contains(target)) {
      return;
    }
    if (target.closest && target.closest('mark.inline-comment-mark')) {
      return;
    }
    if (!panel.hidden) {
      closePanel();
    }
  }

  function onFormSubmit(event) {
    event.preventDefault();
    var nickname = nickInput.value.trim();
    var comment = commentInput.value.trim();
    if (!nickname || !comment) {
      return;
    }
    rememberNickname(nickname);
    if (currentThreadId) {
      addComment(currentThreadId, nickname, comment, null);
      return;
    }
    if (pendingAnchor) {
      createThread(pendingAnchor, nickname, comment);
    }
  }

  function applySnapshot(snapshot) {
    threads = snapshot.val() || {};
    refreshHighlights();
    if (!panel.hidden) {
      if (currentThreadId && !threads[currentThreadId]) {
        closePanel();
        return;
      }
      if (currentThreadId && threads[currentThreadId]) {
        quoteEl.textContent = displayQuote(threads[currentThreadId].quote);
        renderThread();
      }
      positionPanel();
    }
    if (window.location.hash.indexOf('#ic-') === 0 && panel.hidden) {
      var hashId = window.location.hash.slice(4);
      if (threads[hashId]) {
        openThread(hashId);
      }
    }
  }

  function start() {
    var root = contentRoot();
    var article = articleRoot();
    if (!root || !article) {
      return;
    }
    article.classList.add('has-inline-comments');
    nickInput.value = savedNickname();

    addBtn.addEventListener('mousedown', function (event) {
      event.preventDefault();
    });
    addBtn.addEventListener('click', onAddClick);
    closeBtn.addEventListener('click', closePanel);
    backdrop.addEventListener('click', closePanel);
    form.addEventListener('submit', onFormSubmit);
    root.addEventListener('click', onContentClick);
    root.addEventListener('keydown', onContentKeydown);
    document.addEventListener('selectionchange', scheduleToolbar);
    document.addEventListener('mouseup', scheduleToolbar);
    document.addEventListener('touchend', scheduleToolbar);
    document.addEventListener('mousedown', onDocumentPointerDown);
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !panel.hidden) {
        closePanel();
      }
    });
    window.addEventListener('resize', function () {
      if (!toolbar.hidden) {
        var range = selectionRange();
        if (range) {
          placeToolbarForRange(range);
        }
      }
      if (!panel.hidden) {
        positionPanel();
      }
    });
    window.addEventListener('scroll', function () {
      if (!toolbar.hidden) {
        hideToolbar();
      }
      if (!panel.hidden && !isWideLayout()) {
        positionPanel();
      }
    }, true);

    if (typeof firebase === 'undefined' || !firebase.database) {
      showError('评论服务还没准备好，请稍后再试。');
      return;
    }
    database = firebase.database();
    database.ref('inlineComments/' + postId).on('value', applySnapshot, function (err) {
      console.error('inline comments listen failed', err);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
