#!/usr/bin/env python3
"""Emits index.html. The wall and the rain are repetitive, so they are generated
here and the OUTPUT IS COMMITTED: the site itself has no build step. Re-run
this only when the copy or the card decks change:  python3 tools/build-page.py
"""
import html, pathlib, random

WORLD = pathlib.Path('assets/world.svg').read_text(encoding='utf-8')

TITLES = ['Senior Backend Engineer','Product Designer','Data Analyst','Staff Frontend Engineer',
          'DevOps Engineer','Technical Writer','Engineering Manager','Platform Engineer',
          'UX Researcher','Solutions Architect','QA Automation Engineer','Growth Marketer',
          'Security Engineer','iOS Engineer','Site Reliability Engineer']
COS = ['Northwind','Lumen Labs','Halcyon','Brightwater','Meridian','Kestrel','Orbital','Fathom',
       'Greyline','Tessera','Ardent','Copperfield','Vantage','Mosaic','Pillar']
LOCS = ['Remote · EU','Remote · US','Remote · Worldwide','Hybrid · Berlin','Remote · UK',
        'Remote · Americas','Remote · Lisbon','Remote · APAC']
REASONS = ['Residency-locked to Germany','50–60% travel','Requires US hours','Full-time only',
           'Ghost job: reposted 4×','No sponsorship']
N_CARDS = 48
KEEP = {7, 16, 25, 34, 43}

def esc(s): return html.escape(s, quote=True)

def wall_cards():
    # A fixed modulus lines every reason up into its own column, because the
    # grid is 6 wide and there are 6 reasons. Shuffle with a fixed seed instead:
    # irregular at any column count, identical on every build.
    rng = random.Random(20260916)
    reasons = [REASONS[i % len(REASONS)] for i in range(N_CARDS)]
    rng.shuffle(reasons)
    out = []
    for i in range(N_CARDS):
        keep = i in KEEP
        t, c, l = TITLES[(i*7) % 15], COS[(i*11+3) % 15], LOCS[(i*5) % 8]
        cls = 'job job--keep' if keep else 'job'
        card = [f'      <li class="{cls}"{" data-keep" if keep else ""}>']
        card.append(f'        <span class="job__t">{esc(t)}</span>')
        card.append(f'        <span class="job__m">{esc(c)} · {esc(l)}</span>')
        if not keep:
            card.append(f'        <span class="job__stamp" aria-hidden="true"><b>{esc(reasons[i])}</b></span>')
        card.append('      </li>')
        out.append('\n'.join(card))
    return '\n'.join(out)

def rain_cards():
    out = []
    lefts = ['calc(50% - 320px)', 'calc(50% - 155px)', 'calc(50% + 10px)', 'calc(50% + 175px)']
    for k, left in enumerate(lefts):
        st = (f'left:{left};--land:calc(100cqh - 130px);'
              f'animation:fy-fall-stay 11s linear infinite;animation-delay:-{k*2.3+0.7:.2f}s')
        out.append(f'    <div class="rain__card rain__card--keep" style="{st}">'
                   f'<b>{esc(TITLES[(k*7) % 15])}</b><span>{esc(COS[(k*11+3) % 15])} · {esc(LOCS[(k*5) % 8])}</span></div>')
    gl = [3, 11, 19, 27, 35, 43, 51, 59, 67, 75, 83, 91, 8, 30, 55, 80]
    for j, l in enumerate(gl):
        i = 10 + j
        st = f'left:{l}%;animation:fy-fall-out 11s linear infinite;animation-delay:-{(j*11)/len(gl):.2f}s'
        out.append(f'    <div class="rain__card" style="{st}">'
                   f'<b>{esc(TITLES[(i*7) % 15])}</b><span>{esc(COS[(i*11+3) % 15])} · {esc(LOCS[(i*5) % 8])}</span></div>')
    return '\n'.join(out)

QS = [('Passport', 'Which one you hold.'),
      ('Residency', 'Where you can legally live and work.'),
      ('How you invoice', 'Employee, contractor, or your own company.'),
      ('Hours', 'The hours you will actually work.'),
      ('Travel', 'How much, how often.'),
      ('Timezone', 'Where your day starts.')]
STEPS = [('Tell it about you, once.', 'Six questions and your CV.'),
         ('It watches.', 'Every board, every day, while you get on with your life.'),
         ('You get a shortlist.', 'With the CV and cover letter already written.')]
FUNNEL = [(483, 'scanned', '100%', '#2c272e', '#b9b1b8'),
          (34, 'eligible', '64%', '#4a463e', '#d8d0d4'),
          (18, 'worth it', '40%', '#8a7d5c', '#f3eee9'),
          (5, 'applied', '22%', '#e3d3a4', '#0e0b10')]
ROWS = [('Applications sent', 'Callbacks received'), ('More jobs', 'Fewer jobs'),
        ('Keyword matching', 'Can you actually take it?'), ('You search', 'It searches')]

questions = '\n'.join(
    f'        <li class="q"><span class="q__n">0{i+1}</span><div>'
    f'<span class="q__t">{esc(t)}</span><span class="q__s">{esc(s)}</span></div></li>'
    for i, (t, s) in enumerate(QS))
steps = '\n'.join(
    f'        <li class="step" data-reveal><div class="step__n">0{i+1}</div>'
    f'<h3 class="step__t">{esc(t)}</h3><p class="step__s">{esc(s)}</p></li>'
    for i, (t, s) in enumerate(STEPS))
funnel = '\n'.join(
    f'        <li class="rung" style="width:{w}"><span class="rung__fill" style="background:{bg}"></span>'
    f'<span class="rung__lab" style="color:{fg}"><b>{n}</b><span>{esc(lab)}</span></span></li>'
    for n, lab, w, bg, fg in FUNNEL)
rows = '\n'.join(
    f'      <div class="cmp__row" data-reveal><div class="cmp__l">{esc(l)}</div>'
    f'<div class="cmp__r">{esc(r)}</div></div>'
    for l, r in ROWS)

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FindsYou · Stop looking. It finds you work.</title>
<meta name="description" content="FindsYou is a job search that runs without you. It reads every board, throws out the jobs you could never actually take (wrong residency, wrong hours, ghost listings) and hands you the few that are left, with the CV and cover letter already written. In design; not yet built.">
<link rel="canonical" href="https://findsyou.work/">
<meta name="theme-color" content="#0e0b10">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">

<meta property="og:type" content="website">
<meta property="og:site_name" content="FindsYou">
<meta property="og:url" content="https://findsyou.work/">
<meta property="og:title" content="FindsYou · Stop looking. It finds you work.">
<meta property="og:description" content="Fewer jobs. The ones you can actually take, with the documents already written.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="FindsYou · Stop looking. It finds you work.">
<meta name="twitter:description" content="Fewer jobs. The ones you can actually take, with the documents already written.">

<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&amp;family=Manrope:wght@400;500;600&amp;family=IBM+Plex+Mono:wght@400;500&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/findsyou.css">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Organization",
      "@id": "https://findsyou.work/#organization",
      "name": "FindsYou",
      "url": "https://findsyou.work/",
      "email": "hello@findsyou.work",
      "parentOrganization": {{ "@type": "Organization", "name": "Factory Zero", "url": "https://factory0.ventures" }}
    }},
    {{
      "@type": "WebSite",
      "@id": "https://findsyou.work/#website",
      "url": "https://findsyou.work/",
      "name": "FindsYou",
      "description": "A job search that runs without you.",
      "inLanguage": "en",
      "publisher": {{ "@id": "https://findsyou.work/#organization" }}
    }},
    {{
      "@type": "SoftwareApplication",
      "@id": "https://findsyou.work/#app",
      "name": "FindsYou",
      "applicationCategory": "BusinessApplication",
      "operatingSystem": "Web",
      "url": "https://findsyou.work/",
      "publisher": {{ "@id": "https://findsyou.work/#organization" }},
      "releaseNotes": "In design. Not released; no part of this product is available to use yet.",
      "offers": {{ "@type": "Offer", "price": "0", "priceCurrency": "EUR", "availability": "https://schema.org/PreOrder" }}
    }},
    {{
      "@type": "WebPage",
      "@id": "https://findsyou.work/#webpage",
      "url": "https://findsyou.work/",
      "name": "FindsYou · Stop looking. It finds you work.",
      "isPartOf": {{ "@id": "https://findsyou.work/#website" }},
      "about": {{ "@id": "https://findsyou.work/#app" }}
    }}
  ]
}}
</script>
</head>
<body>

<p class="banner">
  Not released: the scan, the filter and the profile exist as code, and none of it is running yet.
  The waitlist is real and is the only thing here that works.
  <a href="#waitlist">Join it</a>, and you will hear once, when there is something to use.
</p>

<nav class="nav">
  <a class="mark" href="#top" aria-label="FindsYou, home">
    <svg class="mark__svg" viewBox="0 0 26 26" aria-hidden="true">
      <path class="mark__v" d="M5 6.5 L13 17 L21 6.5" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <circle class="mark__fall mark__fall--a" cx="9" cy="10" r="1.7"/>
      <circle class="mark__fall mark__fall--b" cx="17" cy="10" r="1.7"/>
      <circle class="mark__catch" cx="13" cy="16" r="2.6"/>
    </svg>
    <span class="mark__word"><b>finds</b><span>you</span><i>.work</i></span>
  </a>
  <div class="nav__links">
    <a href="#wall">the wall</a>
    <a href="#remote">remote</a>
    <a href="#how">how it works</a>
    <a href="#price">price</a>
  </div>
  <a class="btn btn--sm" href="#waitlist">Join the waitlist</a>
</nav>

<main id="top">

  <!-- ------------------------------------------------------------ hero -->
  <section class="hero">
    <div class="rain" aria-hidden="true">
{rain_cards()}
    </div>
    <div class="hero__inner wrap">
      <p class="eyebrow hero__kicker"><b>■</b> every board · six questions · nothing invented</p>
      <h1 class="display">Stop looking. It finds you work.</h1>
      <p class="lede">You&rsquo;ve applied to ninety jobs. Eleven of them would ever have hired you. We find those eleven.</p>
      <a class="btn" href="#waitlist">Show me mine</a>
    </div>
  </section>

  <!-- -------------------------------------------------------- 01 number -->
  <section class="tall" id="number" data-tall="240">
    <div class="stick number">
      <p class="eyebrow">01 / the number</p>
      <p class="number__n" data-count-from="483" data-count-to="18">483</p>
      <p class="number__cap">Jobs scanned in a week. <b>Jobs worth your time.</b></p>
      <p class="eyebrow" style="margin-top:28px;opacity:.6">an illustration: these are not yet real numbers</p>
    </div>
  </section>

  <!-- ---------------------------------------------------------- 02 wall -->
  <section class="tall" id="wall" data-tall="420">
    <div class="stick wall">
      <div class="wall__head eyebrow">
        <span>02 / the wall of no</span>
        <span data-stamp-count>0 of {N_CARDS - len(KEEP)} rejected</span>
      </div>
      <ul class="wall__grid" role="list">
{wall_cards()}
      </ul>
      <p class="wall__yours">These are yours.</p>
    </div>
  </section>

  <!-- -------------------------------------------------------- 03 remote -->
  <section class="band wrap" id="remote">
    <p class="eyebrow">03 / why &ldquo;remote&rdquo; is a lie</p>
    <div class="split" style="margin-top:20px">
      <div class="prose">
        <h2 class="h2">The board says remote. The fine print says Portugal.</h2>
        <p>Or it says 60% travel. Or it says online at 9am in California, five days a week. The listing is remote. The job is not remote for you.</p>
        <p>Nobody filters for this. So we ask you six questions, once.</p>
        <ol class="qs" role="list">
{questions}
        </ol>
        <p class="out">Those six answers eliminate most of the internet.</p>
      </div>
      <div class="mapwrap">
        <div class="map" data-map>{WORLD}</div>
        <p class="mapwrap__foot">
          <span data-map-label>every listing, before your answers</span>
          <span class="mapwrap__num" data-map-num>1,240 jobs &rarr; <b>34</b> you can legally take.</span>
        </p>
      </div>
    </div>
  </section>

  <!-- ----------------------------------------------------------- 04 how -->
  <section class="band wrap" id="how">
    <p class="eyebrow">04 / how it works</p>
    <h2 class="h2" style="margin:20px 0 56px;max-width:20ch">Once, then never again.</h2>
    <ol class="steps" role="list">
{steps}
    </ol>
    <ol class="funnel" role="list" data-reveal>
{funnel}
    </ol>
  </section>

  <!-- --------------------------------------------------------- 05 trust -->
  <section class="tall" id="trust" data-tall="200">
    <div class="stick trust">
      <p class="eyebrow">05 / it won&rsquo;t make things up</p>
      <div class="trust__grid" style="margin-top:20px">
        <p class="trust__claim">Your CV said &ldquo;two years&rdquo;. The system tried to write &ldquo;2 years&rdquo; and refused to print until they matched. Every number traces to something you actually wrote.</p>
        <div class="doc">
          <div>
            <p class="doc__lab">YOUR CV</p>
            <p>Led a distributed team of four for <u>two years</u>, shipping across three timezones.</p>
          </div>
          <div class="doc__step" data-doc="1">
            <p class="doc__lab">DRAFT COVER LETTER</p>
            <p>I bring <mark>2 years</mark> of leading distributed engineering teams.</p>
            <span class="doc__stamp" aria-hidden="true">REFUSED</span>
          </div>
          <div class="doc__step" data-doc="2">
            <p class="doc__lab">PRINTED</p>
            <p>I bring <ins>two years</ins> of leading distributed engineering teams.</p>
            <p class="doc__trace">&#8627; matches &ldquo;two years&rdquo;, line 14 of your CV</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ---------------------------------------------------------- 06 docs -->
  <section class="band wrap" id="docs">
    <p class="eyebrow">06 / what you get</p>
    <div class="split" style="margin-top:20px;align-items:center">
      <div>
        <h2 class="h2">A CV and a cover letter, written for that one job.</h2>
        <p class="lede" style="margin:22px 0 28px;max-width:46ch">Not a template with the company name swapped. Each pair is rebuilt from your CV against the listing, and checked against both.</p>
        <div class="chips">
          <span class="chip">2 pages</span>
          <span class="chip">ATS-checked</span>
          <span class="chip">every number traced</span>
          <span class="chip chip--planned">planned</span>
        </div>
      </div>
      <div class="papers" data-reveal>
        <article class="paper paper--cv">
          <p class="paper__name">Aisha Rahman</p>
          <p class="paper__meta">Senior Backend Engineer · Lisbon</p>
          <div class="paper__lines" aria-hidden="true">
            <i class="hd" style="width:38%"></i><i style="width:100%"></i><i style="width:92%"></i>
            <i style="width:96%"></i><i style="width:70%"></i><i class="hd" style="width:30%"></i>
            <i style="width:100%"></i><i style="width:88%"></i><i style="width:94%"></i><i style="width:60%"></i>
          </div>
          <p class="paper__foot">CV · tailored · 1/2</p>
        </article>
        <article class="paper paper--cl">
          <p class="paper__meta">To the hiring team at Northwind</p>
          <div class="paper__lines" aria-hidden="true">
            <i style="width:100%"></i><i style="width:94%"></i><i style="width:98%"></i><i style="width:52%"></i>
            <i style="width:100%"></i><i style="width:90%"></i><i style="width:96%"></i><i style="width:64%"></i>
            <i style="width:100%"></i><i style="width:40%"></i>
          </div>
          <p class="paper__foot">Cover letter · 1/1</p>
        </article>
      </div>
    </div>
  </section>

  <!-- ------------------------------------------------------- 07 compare -->
  <section class="band wrap wrap--narrow" id="compare">
    <p class="eyebrow" style="margin-bottom:32px">07 / the comparison</p>
    <div class="cmp__head"><div>EVERYONE ELSE</div><div>FINDSYOU</div></div>
{rows}
  </section>

  <!-- --------------------------------------------------------- 08 price -->
  <section class="band wrap wrap--narrow price" id="price">
    <p class="eyebrow" style="margin-bottom:26px">08 / price</p>
    <p class="price__n">Free</p>
    <p class="lede">To scan every board and see your blockers. The report on why each job would have said no is yours to keep.</p>
    <p style="color:var(--dim);font-size:16px;max-width:520px;margin:18px auto 0">Pay only when you want the documents written. <span style="color:var(--ink)">&euro;12 per role</span>, CV and cover letter together. <span class="chip chip--planned" style="display:inline-block;margin-left:6px">planned: nothing is chargeable yet</span></p>
  </section>

  <!-- ------------------------------------------------------- 09 waitlist -->
  <section class="band wrap wait" id="waitlist">
    <h2 class="display" style="font-size:clamp(34px,6vw,84px);max-width:18ch;margin-bottom:28px">You are not bad at applying. You are applying to the wrong jobs.</h2>
    <p class="lede" style="max-width:52ch">Nothing is released yet. Leave your address and you will hear once, when there is something to use.</p>

    <form class="wait__form" id="waitlist-form" data-contact="hello@findsyou.work" data-double-opt-in="false" hidden>
      <div class="field">
        <label class="sr-only" for="waitlist-email">email address</label>
        <input id="waitlist-email" type="email" name="email" required autocomplete="email" placeholder="you@example.com">
        <button class="btn" type="submit">Join the waitlist</button>
      </div>
      <p class="hp" aria-hidden="true"><label>company <input type="text" name="company" tabindex="-1" autocomplete="off"></label></p>
      <p class="form__foot">kept by the <a href="https://cratefield.com">cratefield</a> waitlist module, in a database of its own.</p>
    </form>
    <p class="lede" data-waitlist-nojs style="margin-top:24px">Email <a href="mailto:hello@findsyou.work?subject=FindsYou%20waitlist" style="text-decoration:underline;text-underline-offset:3px">hello@findsyou.work</a> and we will add you by hand.</p>
    <div class="form__status" id="waitlist-status" role="status" aria-live="polite"></div>
  </section>

</main>

<footer class="foot">
  <div class="foot__grid">
    <div>
      <p class="foot__mark">finds<span>you</span><i>.work</i></p>
      <p style="line-height:1.6;max-width:30ch">Fewer jobs. The ones you can actually take, with the documents already written.</p>
    </div>
    <div class="foot__col">
      <p class="foot__h">product</p>
      <a href="#wall">the wall of no</a>
      <a href="#remote">remote, honestly</a>
      <a href="#how">how it works</a>
      <a href="#price">price</a>
    </div>
    <div class="foot__col">
      <p class="foot__h">company</p>
      <a href="mailto:hello@findsyou.work">hello@findsyou.work</a>
      <a href="https://github.com/FindsYou-Work">github</a>
      <a href="https://factory0.ventures">factory zero</a>
    </div>
    <div class="foot__col">
      <p class="foot__h">for machines</p>
      <a href="/llms.txt">llms.txt</a>
      <a href="/sitemap.xml">sitemap.xml</a>
      <a href="/.well-known/security.txt">security.txt</a>
    </div>
    <p class="foot__base">findsyou.work &middot; a <a href="https://factory0.ventures">Factory Zero</a> venture &middot; &copy; 2026</p>
  </div>
</footer>

<script src="/assets/findsyou.js" defer></script>
</body>
</html>
'''

pathlib.Path('index.html').write_text(page, encoding='utf-8')
print(f'index.html written · {len(page):,} bytes · {N_CARDS} wall cards, {len(KEEP)} kept')
