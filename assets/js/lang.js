(function () {
  var STORAGE_KEY = 'siteLang';

  function current() {
    return document.documentElement.classList.contains('lang-en') ? 'en' : 'zh';
  }

  function clearGoogTrans() {
    var host = location.hostname;
    var expires = 'expires=Thu, 01 Jan 1970 00:00:00 GMT';
    var tail = '; path=/; ' + expires;
    document.cookie = 'googtrans=' + tail;
    document.cookie = 'googtrans=' + tail + '; domain=' + host;
    document.cookie = 'googtrans=' + tail + '; domain=.' + host;
  }

  function applyChromeText() {
    var en = current() === 'en';
    var labels = document.querySelectorAll('[data-en-label]');
    var i;
    for (i = 0; i < labels.length; i++) {
      var el = labels[i];
      var zhLabel = el.getAttribute('data-zh-label');
      if (!zhLabel) {
        zhLabel = el.getAttribute('aria-label') || '';
        el.setAttribute('data-zh-label', zhLabel);
      }
      el.setAttribute('aria-label', en ? el.getAttribute('data-en-label') : zhLabel);
    }

    var titles = document.querySelectorAll('[data-en-title]');
    for (i = 0; i < titles.length; i++) {
      var node = titles[i];
      var zhTitle = node.getAttribute('data-zh-title');
      if (!zhTitle) {
        zhTitle = node.getAttribute('title') || '';
        node.setAttribute('data-zh-title', zhTitle);
      }
      node.setAttribute('title', en ? node.getAttribute('data-en-title') : zhTitle);
    }

    var placeholders = document.querySelectorAll('[data-en-placeholder]');
    for (i = 0; i < placeholders.length; i++) {
      var field = placeholders[i];
      var zhPlaceholder = field.getAttribute('data-zh-placeholder');
      if (!zhPlaceholder) {
        zhPlaceholder = field.getAttribute('placeholder') || '';
        field.setAttribute('data-zh-placeholder', zhPlaceholder);
      }
      field.setAttribute('placeholder', en ? field.getAttribute('data-en-placeholder') : zhPlaceholder);
    }

    var buttons = document.querySelectorAll('.lang-toggle-button');
    for (i = 0; i < buttons.length; i++) {
      var on = buttons[i].getAttribute('data-lang') === current();
      buttons[i].setAttribute('aria-pressed', on ? 'true' : 'false');
    }
  }

  document.addEventListener('click', function (event) {
    var button = event.target.closest ? event.target.closest('.lang-toggle-button') : null;
    if (!button) {
      return;
    }
    var next = button.getAttribute('data-lang');
    if (!next || next === current()) {
      return;
    }
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch (err) {
      /* keep the click working if storage is blocked */
    }
    clearGoogTrans();
    location.reload();
  });

  document.addEventListener('DOMContentLoaded', function () {
    clearGoogTrans();
    applyChromeText();
  });
})();
