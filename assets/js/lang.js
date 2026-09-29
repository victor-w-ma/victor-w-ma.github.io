(function () {
  var STORAGE_KEY = 'siteLang';
  var GOOG_VALUE = '/zh-CN/en';

  function current() {
    return document.documentElement.classList.contains('lang-en') ? 'en' : 'zh';
  }

  function cookieVariants(value, expires) {
    var host = location.hostname;
    var tail = '; path=/' + (expires ? '; ' + expires : '');
    document.cookie = value + tail;
    document.cookie = value + tail + '; domain=' + host;
    document.cookie = value + tail + '; domain=.' + host;
  }

  function setGoogTrans() {
    cookieVariants('googtrans=' + GOOG_VALUE, '');
  }

  function clearGoogTrans() {
    cookieVariants('googtrans=', 'expires=Thu, 01 Jan 1970 00:00:00 GMT');
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

  function suppressGoogleBar() {
    var style = document.getElementById('google-translate-fix');
    if (!style) {
      style = document.createElement('style');
      style.id = 'google-translate-fix';
      style.textContent = 'body{top:0!important;position:static!important}html{margin-top:0!important}iframe.skiptranslate,.goog-te-banner-frame{display:none!important}';
      document.head.appendChild(style);
    } else if (style.parentNode && style.parentNode.lastElementChild !== style) {
      style.parentNode.appendChild(style);
    }
  }

  function markTranslationFailed() {
    var notes = document.querySelectorAll('.translation-note.machine');
    var i;
    for (i = 0; i < notes.length; i++) {
      notes[i].textContent = 'Google Translate did not load. This page is still in Chinese.';
    }
  }

  function watchTranslation() {
    var waited = 0;
    suppressGoogleBar();
    var timer = setInterval(function () {
      waited += 400;
      suppressGoogleBar();
      if (document.documentElement.classList.contains('translated-ltr')) {
        clearInterval(timer);
        return;
      }
      if (waited >= 12000) {
        clearInterval(timer);
        markTranslationFailed();
      }
    }, 400);
  }

  function triggerEnglish() {
    var combo = document.querySelector('select.goog-te-combo');
    if (!combo) {
      return false;
    }
    if (combo.value !== 'en') {
      combo.value = 'en';
      combo.dispatchEvent(new Event('change'));
    }
    return true;
  }

  window.googleTranslateElementInit = function () {
    if (!window.google || !google.translate || !google.translate.TranslateElement) {
      return;
    }
    new google.translate.TranslateElement({
      pageLanguage: 'zh-CN',
      includedLanguages: 'en,zh-CN',
      autoDisplay: false,
      layout: google.translate.TranslateElement.InlineLayout.SIMPLE
    }, 'google_translate_element');
    if (current() !== 'en') {
      return;
    }
    watchTranslation();
    setTimeout(function () {
      if (document.documentElement.classList.contains('translated-ltr')) {
        return;
      }
      var fired = false;
      try {
        fired = sessionStorage.getItem('googtransFired') === '1';
      } catch (err) {
        fired = false;
      }
      if (fired) {
        return;
      }
      try {
        sessionStorage.setItem('googtransFired', '1');
      } catch (err) {
        /* still try once */
      }
      var attempts = 0;
      var comboTimer = setInterval(function () {
        attempts += 1;
        if (triggerEnglish() || attempts > 25) {
          clearInterval(comboTimer);
        }
      }, 200);
    }, 1200);
  };

  function loadGoogleTranslate() {
    if (document.getElementById('google-translate-script')) {
      return;
    }
    var script = document.createElement('script');
    script.id = 'google-translate-script';
    script.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    script.async = true;
    document.body.appendChild(script);
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
    try {
      sessionStorage.removeItem('googtransFired');
    } catch (err) {
      /* session storage is optional */
    }
    if (next === 'en') {
      setGoogTrans();
    } else {
      clearGoogTrans();
    }
    location.reload();
  });

  document.addEventListener('DOMContentLoaded', function () {
    applyChromeText();
    if (current() === 'en') {
      setGoogTrans();
      loadGoogleTranslate();
    } else {
      clearGoogTrans();
    }
  });
})();
