/* findsyou.work: reveal, the three scroll scenes, and the waitlist.
   Progressive enhancement throughout: nothing is hidden until this file runs,
   so a blocked or failing script can never leave the page unreadable. The
   whole site is a legible document with JS off. */
(function () {
  'use strict';

  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var clamp = function (v) { return v < 0 ? 0 : v > 1 ? 1 : v; };
  var easeOut = function (t) { return 1 - Math.pow(1 - t, 3); };

  /* ----------------------------------------------------------------- reveal */
  (function () {
    var els = document.querySelectorAll('[data-reveal]');
    if (!els.length || reduced || !('IntersectionObserver' in window)) return;
    // Mark what is already on screen before hiding anything, so nothing flashes.
    var fold = window.innerHeight;
    Array.prototype.forEach.call(els, function (el) {
      if (el.getBoundingClientRect().top < fold) el.classList.add('is-in');
    });
    document.documentElement.classList.add('reveal');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-in');
        io.unobserve(e.target);
      });
    }, { threshold: 0.12 });
    Array.prototype.forEach.call(els, function (el) { io.observe(el); });
  })();

  /* ---------------------------------------------------------- scroll scenes */
  (function () {
    if (reduced) return;

    var number = document.getElementById('number');
    var wall   = document.getElementById('wall');
    var trust  = document.getElementById('trust');
    var remote = document.getElementById('remote');

    var numEl   = number && number.querySelector('[data-count-from]');
    var numStick= number && number.querySelector('.stick');
    var jobs    = wall ? Array.prototype.slice.call(wall.querySelectorAll('.job:not(.job--keep)')) : [];
    var wallStick = wall && wall.querySelector('.stick');
    var counter = wall && wall.querySelector('[data-stamp-count]');
    var docSteps= trust ? Array.prototype.slice.call(trust.querySelectorAll('[data-doc]')) : [];
    var qs      = remote ? Array.prototype.slice.call(remote.querySelectorAll('.q')) : [];
    var mapEl   = remote && remote.querySelector('[data-map]');
    var mapLabel= remote && remote.querySelector('[data-map-label]');
    var mapNum  = remote && remote.querySelector('[data-map-num]');
    var paths   = mapEl ? Array.prototype.slice.call(mapEl.querySelectorAll('path')) : [];

    // Countries where an EU/EEA passport plus residency actually lets you work.
    var KEEP = { 620:1, 724:1, 250:1, 276:1, 528:1, 56:1, 372:1, 826:1, 616:1, 233:1,
                 208:1, 752:1, 246:1, 578:1, 40:1, 756:1, 203:1, 380:1, 428:1, 440:1 };

    var vh = window.innerHeight;
    var lastNum = -1, lastStamped = -1, lastStep = -1;

    function progress(el) {                   // 0..1 through a sticky runway
      var r = el.getBoundingClientRect();
      return clamp(-r.top / Math.max(1, r.height - vh));
    }
    function entering(el, start, end) {        // 0..1 as a block scrolls in
      var r = el.getBoundingClientRect();
      return clamp((start * vh - r.top) / ((start - end) * vh));
    }

    function frame() {
      // 01: the count down from 483 to 18
      if (numEl) {
        var p = progress(number);
        var n = Math.round(483 - 465 * easeOut(p));
        if (n !== lastNum) { numEl.textContent = n; lastNum = n; }
        numStick.classList.toggle('is-settled', p > 0.97);
      }

      // 02: the stamps land in sequence, then the rejected fade away
      if (jobs.length) {
        var pw = progress(wall);
        var want = Math.floor(clamp((pw - 0.04) / 0.62) * jobs.length);
        if (want !== lastStamped) {
          for (var i = 0; i < jobs.length; i++) jobs[i].classList.toggle('is-stamped', i < want);
          if (counter) counter.textContent = want + ' of ' + jobs.length + ' rejected';
          lastStamped = want;
        }
        wallStick.classList.toggle('is-cleared', pw > 0.86);
      }

      // 03: each answer dims another slice of the world
      if (paths.length) {
        var pr = entering(remote, 0.3, -1.2);
        var step = Math.min(6, Math.floor(pr * 7));
        if (step !== lastStep) {
          qs.forEach(function (q, i) { q.classList.toggle('is-on', step > i); });
          paths.forEach(function (path) {
            var id = +path.getAttribute('data-c');
            if (KEEP[id]) { path.classList.toggle('is-keep', step >= 6); return; }
            path.classList.toggle('is-out', step >= ((id * 7) % 6) + 1);
          });
          if (mapLabel) mapLabel.textContent = step === 0
            ? 'every listing, before your answers'
            : step + ' of 6 answered';
          if (mapNum) mapNum.classList.toggle('is-on', step >= 6);
          lastStep = step;
        }
      }

      // 05: the refusal
      if (docSteps.length) {
        var pt = progress(trust);
        docSteps[0].classList.toggle('is-on', pt > 0.22);
        docSteps[0].classList.toggle('is-struck', pt > 0.5);
        docSteps[1].classList.toggle('is-on', pt > 0.74);
      }
    }

    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { ticking = false; frame(); });
    }
    document.addEventListener('scroll', onScroll, { capture: true, passive: true });
    window.addEventListener('resize', function () { vh = window.innerHeight; onScroll(); });
    frame();
  })();

  /* --------------------------------------------------------------- waitlist
     Posts to the Cratefield harness waitlist module running at
     api.findsyou.work. The form is rendered hidden and only revealed here, so
     a browser without fetch is shown the mail fallback instead of a dead form.

     Every join carries a Cloudflare Turnstile token as `captchaToken`; the
     Worker verifies it (bound to findsyou.work and the `waitlist` action) and
     refuses a join without one. The widget script is loaded from here, not
     from a <script> tag, so a blocked or failing load can be told apart and
     said out loud. Tokens are single-use: the widget is reset after every
     attempt, whatever the answer. */
  (function () {
    var form = document.getElementById('waitlist-form');
    var status = document.getElementById('waitlist-status');
    var slot = document.getElementById('waitlist-captcha');
    if (!form || !status || !slot || !window.fetch) return;

    var contact = form.getAttribute('data-contact');
    var doubleOptIn = form.getAttribute('data-double-opt-in') === 'true';
    var button = form.querySelector('button[type="submit"]');
    var label = button.textContent;

    var TURNSTILE_SRC = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=findsyouTurnstileReady';
    var LOAD_TIMEOUT_MS = 10000;
    var widget = null;      // the Turnstile widget id, once rendered
    var token = null;       // the current, unspent token
    var loadFailed = false;

    form.hidden = false;
    var fallback = document.querySelector('[data-waitlist-nojs]');
    if (fallback) fallback.hidden = true;

    function settle(headline, message) {
      status.textContent = '';
      var strong = document.createElement('strong');
      strong.textContent = headline;
      status.appendChild(strong);
      status.appendChild(document.createTextNode(' ' + message));
    }
    function joined(email) {
      form.hidden = true;
      if (doubleOptIn) {
        settle('check your inbox.', 'we sent a confirmation link to ' + email + '. click it to hold your place.');
      } else {
        settle('you’re on the list.', 'we will write to ' + email + ' once, when there is something to use.');
      }
    }
    function retry(headline, message) {
      button.disabled = false;
      button.textContent = label;
      settle(headline, message);
    }
    function unavailable() {
      loadFailed = true;
      if (slot.parentNode) slot.parentNode.hidden = true;   // no empty box where the check should be
      settle('the human check did not load.', 'something (often a content blocker) stopped challenges.cloudflare.com. allow it and reload the page, or email ' + contact + ' and we will add you by hand.');
    }
    // A token is good once. Spend it, then ask Turnstile for a fresh one.
    function spend() {
      token = null;
      if (widget !== null && window.turnstile) window.turnstile.reset(widget);
    }

    window.findsyouTurnstileReady = function () {
      if (loadFailed || !window.turnstile) return;
      widget = window.turnstile.render(slot, {
        sitekey: slot.getAttribute('data-sitekey'),
        action: slot.getAttribute('data-action'),
        theme: 'dark',
        size: 'flexible',
        callback: function (value) { token = value; },
        'expired-callback': function () { token = null; },
        'timeout-callback': function () { token = null; },
        'error-callback': function () {
          token = null;
          settle('the human check hit a snag.', 'it will try again on its own. if it keeps failing, reload the page, or email ' + contact + '.');
        }
      });
    };

    var script = document.createElement('script');
    script.src = TURNSTILE_SRC;
    script.async = true;
    script.defer = true;
    script.onerror = unavailable;
    document.head.appendChild(script);
    setTimeout(function () { if (!window.turnstile && !loadFailed) unavailable(); }, LOAD_TIMEOUT_MS);

    function isCaptchaRefusal(res) {
      return res.json().then(function (problem) {
        return !!(problem && typeof problem.type === 'string' && /\/captcha-failed$/.test(problem.type));
      }, function () { return false; });
    }

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var email = (form.elements.email.value || '').trim();
      if (!email) return;

      // Honeypot: people leave it empty. A bot that fills it learns nothing.
      if ((form.elements.company.value || '').trim()) { joined(email); return; }

      if (loadFailed || !window.turnstile) {
        unavailable();
        return;
      }
      if (!token) {
        settle('one more step.', 'complete the human check below the address, then join again.');
        var frame = slot.querySelector('iframe');
        if (frame) frame.focus();
        return;
      }

      var captchaToken = token;
      button.disabled = true;
      button.textContent = 'joining…';

      fetch('https://api.findsyou.work/v1/waitlist', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ email: email, product: 'findsyou', captchaToken: captchaToken })
      }).then(function (res) {
        spend();
        if (res.ok) { joined(email); return; }
        if (res.status === 400) {
          return isCaptchaRefusal(res).then(function (captcha) {
            if (captcha)
              retry('not verified.', 'the human check did not go through. complete it again and join again, or email ' + contact + '.');
            else
              retry('not added.', 'that address did not look right. check it and try again, or email ' + contact + '.');
          });
        }
        if (res.status === 422)
          retry('not added.', 'that address did not look right. check it and try again, or email ' + contact + '.');
        else if (res.status === 429)
          retry('too many tries.', 'wait a moment and try again, or email ' + contact + '.');
        else
          retry('could not reach the list.', 'try again in a moment, or email ' + contact + ' and we will add you by hand.');
      }, function () {
        spend();
        retry('could not reach the list.', 'try again in a moment, or email ' + contact + ' and we will add you by hand.');
      });
    });
  })();
})();
