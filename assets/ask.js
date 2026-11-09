// ahkira on /ask/. The vetted answers sit in the page as <details>, written ahead of time and read by Amir;
// this file turns them into a chat. Typed questions go to data-api (the ahkira Worker) with a fresh Turnstile
// token each time; with no data-api, no Turnstile or no answer, the vetted answers keep working on their own.
(() => {
  const root = document.getElementById('ask');
  if (!root || typeof ahkira !== 'function') return;  // no script = the plain list of answers still works
  // ONE mascot, and it sits beside ahkira's newest message: it waves at the hello, slides down to the thinking dots,
  // and its face changes there. Older replies keep an empty seat so every bubble lines up.
  const stage = root.querySelector('.ask-mascot'), log = root.querySelector('.ask-log'),
        chips = root.querySelector('.ask-chips'), form = root.querySelector('.ask-form');
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const wait = ms => new Promise(r => setTimeout(r, still ? 0 : ms));
  const EASE = 'cubic-bezier(.2,.8,.2,1)';
  let pose = 'hello', busy = false, rest;

  function onLight() {  // the moon has a light and a dark colouring; pick by the page's own --bg
    const v = getComputedStyle(document.documentElement).getPropertyValue('--bg').trim();
    const m = /^#([0-9a-f]{6})$/i.exec(v);
    if (!m) return !matchMedia('(prefers-color-scheme: dark)').matches;
    const n = parseInt(m[1], 16);
    return (0.2126 * (n >> 16) + 0.7152 * (n >> 8 & 255) + 0.0722 * (n & 255)) / 255 > 0.5;
  }
  function show(p, pop = true) {
    const changed = p !== pose;
    pose = p;
    stage.innerHTML = ahkira({pose: p, anim: !still, onLight: onLight(), shadow: false});
    // a new face springs in instead of snapping
    if (changed && pop && !still) stage.firstElementChild.animate(
      [{transform: 'scale(.84)', opacity: .4}, {transform: 'none', opacity: 1}], {duration: 300, easing: 'cubic-bezier(.3,1.5,.5,1)'});
  }
  // the theme toggle flips attributes on <html>; redraw so the moon keeps its contrast
  new MutationObserver(() => show(pose, false)).observe(document.documentElement, {attributes: true});
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => show(pose, false));

  // Bring a new message into view. A reply taller than the log shows its first line, not its last.
  function follow(el) {
    const max = log.scrollHeight - log.clientHeight;
    const top = Math.max(0, Math.min(max, el.offsetTop + el.offsetHeight - log.clientHeight + 8, el.offsetTop - 8));
    log.scrollTo({top, behavior: still ? 'auto' : 'smooth'});
  }
  // A bot message is a row: a seat for the mascot, then the bubble. Returns the bubble; its row is .parentNode.
  function bubble(who, nodes) {
    const b = document.createElement('div');
    b.className = 'ask-msg ask-' + who;
    b.append(...nodes);
    let row = b;
    if (who === 'bot') {
      row = document.createElement('div');
      row.className = 'ask-turn';
      const seat = document.createElement('div');
      seat.className = 'ask-seat';
      row.append(seat, b);
    }
    log.append(row);
    follow(row);
    return b;
  }
  // Move the mascot to this bubble's seat. It glides from where it was, so the eye follows it down the chat.
  function seat(b) {
    const to = b.parentNode.querySelector('.ask-seat');
    if (!to || stage.parentNode === to) return;
    const from = stage.parentNode?.classList.contains('ask-seat') ? stage.getBoundingClientRect() : null;
    to.append(stage);
    if (!from || still) return;
    const now = stage.getBoundingClientRect(), dx = from.left - now.left, dy = from.top - now.top;
    if (Math.abs(dy) > log.clientHeight) return;  // too far to glide: it just appears in its new seat
    stage.animate([{transform: `translate(${dx}px,${dy}px)`}, {transform: 'none'}], {duration: 460, easing: EASE});
  }
  // The thinking bubble: three bouncing dots beside the mascot, read out as "thinking" to a screen reader.
  function thinking() {
    const p = document.createElement('p');
    p.className = 'ask-dots';
    const sr = document.createElement('span');
    sr.textContent = 'ahkira is thinking';
    p.append(document.createElement('i'), document.createElement('i'), document.createElement('i'), sr);
    const b = bubble('bot', [p]);
    seat(b);
    show('think');
    return b;
  }
  // The thinking bubble turns into the answer in place: no bubble is removed, so nothing below it jumps twice.
  // The whole answer is laid out first with the unread part see-through, so the bubble takes its final size in one
  // smooth grow and words never hop to the next line while they type.
  async function speak(b, nodes) {
    const before = b.getBoundingClientRect();
    const jobs = [];
    for (const n of nodes) {
      if (!still && !n.querySelector('a')) {
        const text = n.textContent, shown = document.createTextNode(''), ghost = document.createElement('span');
        ghost.className = 'ask-ghost';
        ghost.textContent = text;
        n.replaceChildren(shown, ghost);
        jobs.push(() => type(n, text, shown, ghost));
      } else {
        if (!still) n.classList.add('ask-later');
        jobs.push(async () => { n.classList.remove('ask-later'); });
      }
    }
    b.replaceChildren(...nodes);
    const after = b.getBoundingClientRect();
    if (!still && b.parentNode.isConnected) {
      const cut = (a, z) => Math.max(0, Math.round(z - a));
      b.animate([{clipPath: `inset(0 ${cut(before.width, after.width)}px ${cut(before.height, after.height)}px 0 round 4px 14px 14px 14px)`},
                 {clipPath: 'inset(0 0 0 0 round 4px 14px 14px 14px)'}], {duration: 320, easing: EASE});
    }
    follow(b.parentNode);
    for (const job of jobs) await job();
  }
  // The log is NOT a live region: the typing animation rewrites a bubble every few milliseconds and a screen reader
  // would read every step. A finished reply is announced once, through this separate polite status line.
  const say = root.querySelector('.ask-sr');
  function announce(text) {
    if (!say) return;
    say.textContent = '';
    setTimeout(() => { say.textContent = text; }, 60);
  }
  // Letters fill in on the screen's own frame clock: smooth at any refresh rate, about two seconds at most for a
  // long paragraph. A background tab gets no frames, so a hidden tab skips straight to the end instead of waiting.
  function type(p, text, shown, ghost) {
    return new Promise(done => {
      const rate = Math.max(0.16, text.length / 2200);  // letters per millisecond
      let t0 = null, over = false;
      const step = now => {
        if (over) return;  // a frame queued before a hidden-tab finish must not touch the finished (maybe linked) text
        t0 ??= now;
        const n = document.hidden ? text.length : Math.min(text.length, Math.ceil((now - t0) * rate));
        shown.data = text.slice(0, n);
        ghost.textContent = text.slice(n);
        if (n < text.length) return requestAnimationFrame(step);
        over = true;
        document.removeEventListener('visibilitychange', hide);
        p.textContent = text;
        done();
      };
      const hide = () => { if (document.hidden) step(performance.now()); };
      document.addEventListener('visibilitychange', hide);
      if (document.hidden) step(0); else requestAnimationFrame(step);
    });
  }
  // Own-site URLs and his email only; built as DOM nodes, never innerHTML. Trailing punctuation stays text.
  function linkify(p) {
    const text = p.textContent, re = /\b(?:https?:\/\/)?ahk02x\.dev(?:\/[\w\-./#]*)?|\bamir@ahk02x\.com\b/g;
    let last = 0, m, out = [];
    while ((m = re.exec(text))) {
      const s = m[0].replace(/[.,)]+$/, '');
      const a = document.createElement('a');
      a.textContent = s;
      a.href = s.includes('@') ? 'mailto:' + s : 'https://' + s.replace(/^https?:\/\//, '');
      out.push(text.slice(last, m.index), a);
      last = m.index + s.length;
    }
    if (!out.length) return;
    out.push(text.slice(last));
    p.replaceChildren(...out);
  }
  function lock(on) {
    root.querySelectorAll('.ask-chips button, .ask-form button').forEach(b => { b.disabled = on; });
  }
  async function answer(d, btn) {
    if (busy) return;
    busy = true; clearTimeout(rest);
    lock(true);
    try {
      const q = document.createElement('p');
      q.textContent = d.querySelector('summary').textContent;
      bubble('you', [q]);
      await wait(160);
      const b = thinking();
      await wait(750);
      show('done');
      await speak(b, [...d.children].filter(n => n.tagName !== 'SUMMARY').map(n => n.cloneNode(true)));
      announce(b.textContent);
      btn.classList.add('asked');
      rest = setTimeout(() => show('idle'), 1600);
    } finally {
      lock(false);
      busy = false;
    }
  }

  // ---- typed questions -------------------------------------------------------------------------------------
  const api = root.dataset.api, sitekey = root.dataset.sitekey;
  const chat = crypto.randomUUID ? crypto.randomUUID() : null;
  const history = [];          // only typed turns; the last two exchanges go along as context
  let widget = null, pending = null, sent = 0;   // sent = questions that really went to the server this visit
  const REPLY = {
    nap: 'ahkira is curled up for a nap. The answers above are still wide awake.',
    limited: "That's a lot of questions for one minute. Give me a moment, then try again.",
    broken: "I couldn't reach my brain just now. The answers above still work.",
    check: "The quick bot check didn't go through, so I didn't send that. Please try again.",
  };

  // One place ends a bot check, whichever way it ends: its own timer stops and the "tick the box" note goes away.
  function settle(how, value) {
    const p = pending;
    if (!p) return;
    pending = null;
    clearTimeout(p.timer);
    root.querySelector('.ask-check')?.remove();
    p[how](value);
  }
  function token() {
    // A Turnstile token is single use: run the widget, wait for it, reset it for next time.
    return new Promise((resolve, reject) => {
      if (!window.turnstile || widget === null) return reject(new Error('no turnstile'));
      settle('reject', new Error('superseded'));
      // Two minutes: long enough for a person who is shown the checkbox to find it and tick it. The timer belongs to
      // THIS check and is cleared when it settles, so an old one can never fail a later check.
      pending = { resolve, reject, timer: setTimeout(() => settle('reject', new Error('turnstile timeout')), 120000) };
      try { turnstile.reset(widget); turnstile.execute(widget); } catch (e) { settle('reject', e); }
    });
  }
  function mountTurnstile(tries = 0) {
    if (window.turnstile) {
      widget = turnstile.render(root.querySelector('.ask-ts'), {
        sitekey, action: 'ask', execution: 'execute', appearance: 'interaction-only', size: 'flexible', 'refresh-expired': 'manual',
        callback: t => settle('resolve', t),
        'error-callback': () => { settle('reject', new Error('turnstile error')); return true; },
        'timeout-callback': () => settle('reject', new Error('turnstile timeout')),
        // Turnstile sometimes wants a click. Say so, or the visitor just watches "thinking…" with no idea why.
        'before-interactive-callback': () => {
          if (root.querySelector('.ask-check')) return;
          const p = document.createElement('p');
          p.textContent = 'One quick check that you are a person: tick the box under the chat.';
          bubble('bot', [p]).parentNode.classList.add('ask-check');
          announce(p.textContent);
        },
        'after-interactive-callback': () => { root.querySelector('.ask-check')?.remove(); },
      });
      form.hidden = false;
    } else if (tries < 40) setTimeout(() => mountTurnstile(tries + 1), 250);
    // No Turnstile after 10 s (blocked, offline): the box stays hidden and the vetted answers carry on.
  }

  async function ask(text) {
    if (busy) return;
    busy = true; clearTimeout(rest); lock(true);
    let reply = REPLY.broken, state = 'broken';
    try {
      const q = document.createElement('p');
      q.textContent = text;
      bubble('you', [q]);
      await wait(160);
      const waiting = thinking();
      let cut;
      try {
        // The server wants visitor-first, alternating turns under 4,000 characters: keep the newest pairs that fit.
        let turns = [...history, { role: 'user', content: text }].slice(-5);
        while (turns.length > 1 && turns.reduce((n, t) => n + t.content.length, 0) > 3600) turns = turns.slice(2);
        let pass;
        try { pass = await token(); } catch { state = 'check'; throw new Error('check'); }
        // The Worker gives the model 25 s; 35 s here means a hung connection ends in "broken", never in a page that stays locked.
        const stop = new AbortController();
        cut = setTimeout(() => stop.abort(), 35000);
        sent += 1;
        const res = await fetch(api, {
          method: 'POST', headers: { 'content-type': 'application/json' }, credentials: 'same-origin', signal: stop.signal,
          body: JSON.stringify({ messages: turns, turnstile: pass, chat, turn: sent }),
        });
        const body = await res.json().catch(() => ({}));
        state = body.state || (res.status === 429 ? 'limited' : 'broken');
        reply = typeof body.reply === 'string' && body.reply ? body.reply : REPLY[state] || REPLY.broken;
      } catch { if (state === 'check') reply = REPLY.check; /* otherwise stays "broken" */ }
      finally { clearTimeout(cut); }
      // ok = a happy face while it answers; napping = asleep, and it stays asleep; anything else = calm, never the red moon
      show(state === 'ok' ? 'done' : state === 'nap' ? 'sleep' : 'idle');
      const p = document.createElement('p');
      p.textContent = reply;
      await speak(waiting, [p]);
      linkify(p);
      announce(reply);
      if (state === 'ok') {
        // The server refuses an assistant turn over 1,200 characters, and one refusal would break every later question.
        history.push({ role: 'user', content: text }, { role: 'assistant', content: reply.slice(0, 1200) });
      }
      if (state !== 'nap') rest = setTimeout(() => show('idle'), 1600);
      return state;
    } finally {
      // However this ends, the page must never stay locked.
      lock(false);
      busy = false;
    }
  }

  if (form && api && sitekey) {
    const box = form.querySelector('textarea'), count = form.querySelector('.ask-count');
    const tally = () => { count.textContent = box.value.length > 400 ? `${box.value.length} / 500` : ''; };
    box.addEventListener('input', tally);
    box.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); form.requestSubmit(); }
    });
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const text = box.value.trim();
      if (!text || busy) return;
      box.value = ''; tally();
      const sentText = text.slice(0, 500);
      const state = await ask(sentText);
      // The bot check failed, so nothing was sent: the words go back in the box instead of being lost.
      if (state === 'check' && !box.value) { box.value = sentText; tally(); }
      box.focus();
    });
    mountTurnstile();
  }

  // Phones get four questions and a "More questions" button instead of a wall of chips above the text box.
  const SHOW = 4;
  [...root.querySelectorAll('.ask-faq details')].forEach((d, i) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = d.querySelector('summary').textContent;
    btn.addEventListener('click', () => answer(d, btn));
    if (i >= SHOW) btn.hidden = true;
    chips.append(btn);
  });
  if (chips.children.length > SHOW) {
    const more = document.createElement('button');
    more.type = 'button';
    more.className = 'ask-more';
    more.textContent = 'More questions';
    more.addEventListener('click', () => {
      chips.querySelectorAll('button[hidden]').forEach(b => { b.hidden = false; });
      more.remove();
    });
    chips.append(more);
  }
  const hello = root.querySelector('.ask-hello');
  if (hello) seat(bubble('bot', [hello.cloneNode(true)]));
  root.classList.add('ask-on');
  show('hello');
  rest = setTimeout(() => show('idle'), 2600);
})();
