#!/usr/bin/env python3
"""Gera o site estático do Ofício a partir de data/tutoriais.json.

Uso: python3 tools/build.py   (sem dependências; o resultado já fica versionado,
então o GitHub Pages publica direto da branch main, sem etapa de build.)
"""
import json, html, os, datetime, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://mrmms22.github.io/oficio-tutoriais/"
SITE = "Ofício"
VER = "5"
# Imagens dos passos: "datajs" = cada tutorial ganha img/<id>/passos.js com as imagens em data URI
# (só texto, publicável pelo conector do GitHub); "files" = <img src="img/<id>/<n>.webp"> direto.
IMG_MODE = os.environ.get("OFICIO_IMG_MODE", "datajs")  # muda para invalidar cache de CSS/JS

data = json.loads((ROOT / "data/tutoriais.json").read_text(encoding="utf-8"))
CATS = {
    "casa": {"label": "Casa", "desc": "Limpeza, cozinha, banheiro, roupa e pequenos reparos."},
    "jardim": {"label": "Jardim", "desc": "Vaso, horta, rega, poda e pragas sem veneno forte."},
    "eletronicos": {"label": "Eletrônicos", "desc": "Celular, Wi-Fi, PC, TV, GPS e cabos."},
}
e = lambda s: html.escape(str(s), quote=True)

def svg(path, cls="icon", extra=""):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" {extra}>{path}</svg>'

I = {
    "casa": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
    "jardim": '<path d="M12 21v-8"/><path d="M12 13c0-4 3-7 8-7 0 4-3 7-8 7Z"/><path d="M12 15c0-3-2.5-5.5-7-5.5 0 3 2.5 5.5 7 5.5Z"/>',
    "eletronicos": '<rect x="6" y="2.5" width="12" height="19" rx="2.5"/><path d="M11 18h2"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11"/><path d="M4 6h.01M4 12h.01M4 18h.01"/>',
    "box": '<path d="M21 8 12 3 3 8v8l9 5 9-5Z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
    "warn": '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
    "tip": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2V17h5v-1.1c0-.8.4-1.5 1-2A6 6 0 0 0 12 3Z"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "moon": '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/>',
    "share": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/>',
    "print": '<path d="M6 9V3h12v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M6 14h12v7H6z"/>',
    "check": '<path d="m5 12 5 5L20 7"/>',
    "back": '<path d="M19 12H5M12 19l-7-7 7-7"/>',
    "bolt": '<path d="M13 2 4 14h7l-1 8 9-12h-7Z"/>',
}

def head(title, desc, path, prefix, ogtype="website", extra=""):
    url = BASE + path
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta name="theme-color" content="#0b0c0a">
<meta name="view-transition" content="same-origin">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{BASE}assets/og.svg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="{prefix}manifest.webmanifest">
<script>(function(){{try{{var t=localStorage.getItem("oficio:tema");t=t?JSON.parse(t):null}}catch(e){{}}if(!t)t=matchMedia("(prefers-color-scheme: light)").matches?"light":"dark";document.documentElement.setAttribute("data-theme",t)}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Instrument+Serif:ital@0;1&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/style.css?v={VER}">
{extra}</head>
<body>
<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<div class="fx-bg" aria-hidden="true"><i class="b1"></i><i class="b2"></i><i class="b3"></i><canvas id="fx-particles"></canvas><span class="fx-grid"></span></div>
<div class="readbar" aria-hidden="true"><i></i></div>
<header class="top"><div class="wrap top-in">
  <a class="brand" href="{prefix}" aria-label="Ofício — início"><span class="mark" aria-hidden="true">Of</span><span><b>Ofício</b><small>casa · quintal · cabo</small></span></a>
  <nav aria-label="Principal"><a href="{prefix}#tutoriais">Tutoriais</a><a href="{prefix}?cat=casa#tutoriais">Casa</a><a href="{prefix}?cat=jardim#tutoriais">Jardim</a><a href="{prefix}?cat=eletronicos#tutoriais">Eletrônicos</a></nav>
  <a class="iconbtn" href="{prefix}#busca" aria-label="Buscar tutoriais" title="Buscar">{svg(I["search"])}</a>
  <button class="iconbtn" type="button" data-theme-toggle aria-label="Trocar tema">{svg(I["sun"],"icon theme-light")}{svg(I["moon"],"icon theme-dark")}</button>
</div></header>
'''

def foot(prefix):
    return f'''<footer class="foot-site"><div class="wrap">
  <span>Ofício · {len(data)} tutoriais práticos · grátis, sem conta e sem anúncio.</span>
  <a class="bmc" data-bmc hidden target="_blank" rel="noopener">☕ Apoie com um café</a>
  <span>Por <a href="https://marcel-machado.netlify.app" rel="author">Marcel Machado</a> · <a href="https://github.com/MrMMs22/oficio-tutoriais">código no GitHub</a></span>
</div></footer>
<script src="{prefix}assets/config.js?v={VER}" defer></script>
<script src="{prefix}assets/app.js?v={VER}" defer></script>
</body>
</html>
'''

def meta_bits(t):
    n = len(t["passos"])
    return f'<span>{svg(I["clock"])}{t["minutos"]} min</span><span>{svg(I["list"])}{n} passo{"s" if n!=1 else ""}</span>' + (f'<span class="w" title="Tem alerta de segurança">{svg(I["warn"])}alerta</span>' if t["aviso"] else "")

def card(t, i, prefix, li=True, idx=None):
    c = t["tema"]
    inner = f'''<article class="card c-{c}">
  <div class="row"><span class="num">{i:02d}</span><span class="pill">{svg(I[c])}{CATS[c]["label"]}</span></div>
  <h3><a href="{prefix}t/{t["id"]}/">{e(t["titulo"])}</a></h3>
  <p>{e(t["resumo"])}</p>
  <div class="foot">{meta_bits(t)}</div>
</article>'''
    if not li:
        return f"<li>{inner}</li>"
    extra = " ".join(t["passos"] + t["material"] + [t["dica"], t["aviso"], t["id"].replace("-", " ")])
    return f'<li data-id="{t["id"]}" data-cat="{c}" data-min="{t["minutos"]}" data-idx="{i}" data-steps="{len(t["passos"])}" data-title="{e(t["titulo"])}" data-extra="{e(extra)}">{inner}</li>'

out = {}

# ---------- home ----------
counts = {k: sum(1 for t in data if t["tema"] == k) for k in CATS}
avg = round(sum(t["minutos"] for t in data) / len(data))
quick = sum(1 for t in data if t["minutos"] <= 10)
ld_home = {
    "@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE, "inLanguage": "pt-BR",
    "potentialAction": {"@type": "SearchAction", "target": BASE + "?q={q}", "query-input": "required name=q"},
}
home = head(f"Ofício — {len(data)} tutoriais práticos de casa, jardim e eletrônicos",
            f"{len(data)} tutoriais curtos e grátis: limpar, consertar, plantar e resolver o celular, o Wi-Fi e o PC. Passo a passo, material e alertas de segurança.",
            "", "", extra=f'<script>(function(){{var m=location.hash.match(/^#\\/t\\/([^/?#]+)/);if(m)location.replace("t/"+encodeURIComponent(decodeURIComponent(m[1]))+"/")}})();</script>\n<script type="application/ld+json">{json.dumps(ld_home, ensure_ascii=False)}</script>\n')
home += f'''<main id="conteudo" class="wrap">
<section class="hero reveal" aria-labelledby="titulo">
  <div>
    <span class="kicker">Caderno prático · edição 2026</span>
    <h1 id="titulo">Noventa ofícios. <em>Sem enrolação.</em></h1>
    <p class="lead">Limpar privada, trocar lâmpada, plantar manjericão, passar GPX no Garmin. Passo a passo curto, com o material e o alerta de quando a coisa queima a mão. Grátis, sem conta e sem app.</p>
    <form class="searchbox" role="search" action="./" onsubmit="return false">
      <label for="q" class="sr-only">Buscar tutoriais</label>
      {svg(I["search"])}
      <input id="q" name="q" type="search" placeholder="privada, lâmpada, Garmin, vaso…" autocomplete="off" enterkeyhint="search">
      <kbd aria-hidden="true">/</kbd><button type="button" class="clear">Limpar</button>
    </form>
  </div>
  <div class="stats" aria-label="Números">
    <div class="stat"><strong>{len(data)}</strong><span>tutoriais</span></div>
    <div class="stat"><strong>{quick}</strong><span>em até 10 min</span></div>
    <div class="stat"><strong>~{avg}</strong><span>min em média</span></div>
  </div>
</section>
<div class="cats" id="busca" role="group" aria-label="Categorias">
''' + "".join(f'''  <button type="button" class="cat c-{k}" data-cat-card="{k}" aria-pressed="false"><span class="ico">{svg(I[k],"")}</span><span><b>{v["label"]}</b><span>{counts[k]} tutoriais · {e(v["desc"])}</span></span></button>
''' for k, v in CATS.items()) + f'''</div>
<div class="ad-slot" data-ad="home" hidden></div>
<section id="tutoriais" aria-labelledby="lista-titulo">
  <h2 id="lista-titulo" class="sr-only">Tutoriais</h2>
  <div class="toolbar">
    <div class="chips" role="group" aria-label="Filtrar por categoria">
      <button type="button" class="chip" data-filter="todos" aria-pressed="true">Todos <small>{len(data)}</small></button>
''' + "".join(f'      <button type="button" class="chip" data-filter="{k}" aria-pressed="false">{v["label"]} <small>{counts[k]}</small></button>\n' for k, v in CATS.items()) + f'''      <button type="button" class="chip" data-rapido aria-pressed="false">{svg(I["bolt"])}Até 10 min</button>
    </div>
    <span class="spacer"></span>
    <p class="count" data-count aria-live="polite">{len(data)} tutoriais</p>
    <label class="sr-only" for="ordem">Ordenar</label>
    <select id="ordem" class="select"><option value="padrao">Ordem do caderno</option><option value="rapidos">Mais rápidos</option><option value="az">A–Z</option></select>
  </div>
  <ul class="grid" id="lista">
''' + "\n".join(card(t, i + 1, "") for i, t in enumerate(data)) + f'''
  </ul>
  <div class="empty" data-empty hidden><b>Nada com esse nome.</b>Tente outra palavra, como “vaso”, “Wi-Fi” ou “mofo”.<p><button type="button" class="btn" data-reset>Limpar busca e filtros</button></p></div>
</section>
<section class="about" aria-label="Sobre o Ofício">
  <div><h2>Curto de propósito</h2><p>Cada tutorial cabe numa tela: o que você precisa, os passos e o que não fazer.</p></div>
  <div><h2>Segurança antes</h2><p>Quando tem choque, produto químico ou calor no meio, o alerta aparece antes dos passos.</p></div>
  <div><h2>Marque o que fez</h2><p>Toque em cada passo para marcar. O progresso fica salvo só no seu aparelho.</p></div>
</section>
</main>
''' + foot("")
out["index.html"] = home

# ---------- tutoriais ----------
bycat = {k: [t for t in data if t["tema"] == k] for k in CATS}
num = {t["id"]: i + 1 for i, t in enumerate(data)}
for t in data:
    c = t["tema"]; lst = bycat[c]; k = lst.index(t)
    prv, nxt = lst[k - 1], lst[(k + 1) % len(lst)]
    rel = [lst[(k + j) % len(lst)] for j in range(2, 5)]
    pre = "../../"
    n = len(t["passos"])
    desc = f'{t["resumo"]} Passo a passo em {n} etapas, cerca de {t["minutos"]} min.'
    ld = {
        "@context": "https://schema.org", "@type": "HowTo", "name": t["titulo"], "description": t["resumo"],
        "inLanguage": "pt-BR", "totalTime": f'PT{t["minutos"]}M', "url": BASE + f't/{t["id"]}/',
        "supply": [{"@type": "HowToSupply", "name": m} for m in t["material"]],
        "step": [{"@type": "HowToStep", "position": i + 1, "text": p} for i, p in enumerate(t["passos"])],
    }
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": SITE, "item": BASE},
        {"@type": "ListItem", "position": 2, "name": CATS[c]["label"], "item": BASE + f"?cat={c}"},
        {"@type": "ListItem", "position": 3, "name": t["titulo"]}]}
    toc = [("material", "O que você precisa")]
    if t["aviso"]: toc.append(("atencao", "Atenção"))
    toc.append(("passos", "Passo a passo"))
    if t["dica"]: toc.append(("dica", "Dica"))
    p = head(f'{t["titulo"]} — {SITE}', desc, f't/{t["id"]}/', pre, "article",
             extra=f'<script type="application/ld+json">{json.dumps([ld, crumbs], ensure_ascii=False)}</script>\n')
    p += f'''<main id="conteudo" class="wrap">
<article data-id="{t["id"]}" class="c-{c}">
<ol class="crumbs" aria-label="Você está em"><li><a href="{pre}">Início</a></li><li><a href="{pre}?cat={c}#tutoriais">{CATS[c]["label"]}</a></li><li aria-current="page">Nº {num[t["id"]]:02d}</li></ol>
<header class="art-head reveal">
  <span class="pill">{svg(I[c])}{CATS[c]["label"]}</span>
  <h1>{e(t["titulo"])}</h1>
  <p class="lead">{e(t["resumo"])}</p>
  <ul class="meta" aria-label="Resumo">
    <li>{svg(I["clock"])}Cerca de {t["minutos"]} min</li>
    <li>{svg(I["list"])}{n} passo{"s" if n!=1 else ""}</li>
    <li>{svg(I["box"])}{len(t["material"])} {"itens" if len(t["material"])!=1 else "item"}</li>
  </ul>
  <div class="actions">
    <button type="button" class="btn" data-share>{svg(I["share"])}Compartilhar</button>
    <button type="button" class="btn" data-print>{svg(I["print"])}Imprimir</button>
  </div>
</header>
<div class="layout">
<div>
  <section class="sec" id="material" aria-labelledby="h-material">
    <h2 id="h-material">O que você precisa <small>{len(t["material"])}</small></h2>
    <ul class="checklist">
''' + "".join(f'      <li><label><input type="checkbox"><span>{e(m)}</span></label></li>\n' for m in t["material"]) + "    </ul>\n  </section>\n"
    if t["aviso"]:
        p += f'''  <div class="callout warn" id="atencao" role="note">{svg(I["warn"])}<div><b>Atenção</b><p>{e(t["aviso"])}</p></div></div>\n'''
    p += '  <div class="ad-slot" data-ad="tutorialTop" hidden></div>\n'
    imgs = t.get("imagens") or []
    def fig(i):
        if i >= len(imgs) or not imgs[i]: return ""
        im = imgs[i]
        src = f'{pre}{im["arquivo"]}'
        if IMG_MODE == "datajs":
            return f'<figure class="step-fig"><img data-img="{i}" alt="{e(im["alt"])}" width="1024" height="768" decoding="async"></figure>'
        return f'<figure class="step-fig"><img src="{src}" alt="{e(im["alt"])}" width="1024" height="768" loading="lazy" decoding="async"></figure>'
    dj = f' data-imgjs="{pre}img/{t["id"]}/passos.js?v={VER}"' if IMG_MODE == "datajs" and any(imgs) else ""
    p += f'''  <section class="sec" id="passos" aria-labelledby="h-passos"{dj}>
    <h2 id="h-passos">Passo a passo <small>{n}</small></h2>
    <ol class="steps">
''' + "".join(f'''      <li class="step{' has-fig' if fig(i) else ''}"><span class="n" aria-hidden="true">{i+1}</span><p><span class="sr-only">Passo {i+1}: </span>{e(s)}</p><button type="button" class="tick" aria-pressed="false" aria-label="Marcar passo {i+1} como feito">{svg(I["check"])}<span class="tick-txt">Marcar</span></button>{fig(i)}</li>
''' for i, s in enumerate(t["passos"])) + "    </ol>\n  </section>\n"
    p += '  <div class="finish" role="status"><b>Pronto! 🎉</b><p>Todos os passos marcados. <button type="button" class="linkbtn" data-reset-steps>Recomeçar</button></p></div>\n'
    if t["dica"]:
        p += f'''  <div class="callout tip" id="dica" role="note">{svg(I["tip"])}<div><b>Dica</b><p>{e(t["dica"])}</p></div></div>\n'''
    p += '  <aside class="support" data-bmc-box hidden><div><b>Este tutorial ajudou?</b><p>O Ofício é grátis e sem cadastro. Se quiser, pague um café pro autor.</p></div><a class="btn primary" data-bmc target="_blank" rel="noopener">☕ Buy me a coffee</a></aside>\n'
    p += '  <div class="ad-slot" data-ad="tutorialBottom" hidden></div>\n'
    p += f'''  <nav class="pager" aria-label="Mais de {CATS[c]["label"]}">
    <a class="prev" href="{pre}t/{prv["id"]}/" rel="prev"><small>← Anterior em {CATS[c]["label"]}</small><b>{e(prv["titulo"])}</b></a>
    <a class="next" href="{pre}t/{nxt["id"]}/" rel="next"><small>Próximo em {CATS[c]["label"]} →</small><b>{e(nxt["titulo"])}</b></a>
  </nav>
</div>
<aside class="side" aria-label="Seu progresso">
  <div class="panel">
    <h2>Seu progresso</h2>
    <div class="progress" aria-hidden="true"><i></i></div>
    <div class="prog-label"><span data-prog>0 de {n} passos</span><button type="button" class="linkbtn" data-reset-steps>Zerar</button></div>
  </div>
  <nav class="panel toc-panel" aria-label="Nesta página">
    <h2>Nesta página</h2>
    <ul class="toc">
''' + "".join(f'      <li><a href="#{a}">{b}</a></li>\n' for a, b in toc) + f'''    </ul>
  </nav>
</aside>
</div>
</article>
<section class="related" aria-labelledby="h-rel">
  <h2 id="h-rel">Mais de {CATS[c]["label"]}</h2>
  <ul class="grid">
''' + "\n".join(card(r, num[r["id"]], pre, li=False) for r in rel) + '''
  </ul>
</section>
</main>
''' + foot(pre)
    out[f't/{t["id"]}/index.html'] = p

# ---------- 404 (caminhos absolutos: o Pages serve em qualquer URL) ----------
ABS = "/oficio-tutoriais/"
nf = head("Página não encontrada — Ofício", "Essa página não existe. Busque entre os tutoriais do Ofício.", "404.html", ABS,
          extra='<meta name="robots" content="noindex">\n')
nf += f'''<main id="conteudo" class="wrap nf">
  <div class="big" aria-hidden="true">404</div>
  <h1>Essa página sumiu do caderno.</h1>
  <p>O link pode estar errado ou o tutorial mudou de lugar. Busque abaixo ou volte ao início.</p>
  <form class="searchbox" role="search" action="{ABS}" method="get">
    <label for="q404" class="sr-only">Buscar tutoriais</label>{svg(I["search"])}
    <input id="q404" name="q" type="search" placeholder="privada, lâmpada, Garmin, vaso…" autocomplete="off">
  </form>
  <p style="margin-top:22px"><a class="btn primary" href="{ABS}">{svg(I["back"])}Ver os {len(data)} tutoriais</a></p>
</main>
''' + foot(ABS)
out["404.html"] = nf

# ---------- URL antiga tutoriais/tutorial.html ----------
out["tutoriais/tutorial.html"] = f'''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Ofício</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{BASE}">
<script>(function(){{var s=new URLSearchParams(location.search).get("id");var h=location.hash.replace(/^#\\/?(t\\/)?/,"");var id=s||h;location.replace("../"+(id?"t/"+encodeURIComponent(id)+"/":""))}})();</script>
<noscript><meta http-equiv="refresh" content="0; url=../"></noscript>
</head><body><p><a href="../">Ir para o Ofício</a></p></body></html>
'''

# ---------- sitemap, robots, manifest ----------
today = datetime.date.today().isoformat()
urls = [BASE] + [BASE + f't/{t["id"]}/' for t in data]
out["sitemap.xml"] = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n"
out["robots.txt"] = f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n"
out["manifest.webmanifest"] = json.dumps({"name": "Ofício — tutoriais práticos", "short_name": "Ofício", "lang": "pt-BR", "start_url": "./", "scope": "./", "display": "standalone", "background_color": "#0b0c0a", "theme_color": "#0b0c0a", "icons": [{"src": "assets/favicon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"}]}, ensure_ascii=False, indent=1) + "\n"
out[".nojekyll"] = ""

if IMG_MODE == "datajs":
    import base64
    for t in data:
        imgs = t.get("imagens") or []
        if not any(imgs): continue
        uris = []
        for im in imgs:
            f = ROOT / im["arquivo"] if im else None
            uris.append("data:image/webp;base64," + base64.b64encode(f.read_bytes()).decode() if f and f.exists() else "")
        out[f'img/{t["id"]}/passos.js'] = "/* Imagens dos passos de " + t["id"] + " (WebP em data URI; gerado por tools/build.py) */\n(window.OFICIO_IMGS=window.OFICIO_IMGS||{})[" + json.dumps(t["id"]) + "]=" + json.dumps(uris) + ";\n"

for rel, txt in out.items():
    f = ROOT / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(txt, encoding="utf-8")
print(f"{len(out)} arquivos gerados ({len(data)} tutoriais)")
