#!/usr/bin/env python3
"""build.py – writes every page of the site from tasks.json and the templates in templates/.

    python3 build.py

Pages written: index.html, <course>/index.html, <course>/<task id>.html and
grafika-inxhinierike/teoria.html. Adding an animation later means: copy the file into
animacione/, set "animation": "<file>" (and "steps") on the task in tasks.json, run this again.
"""
import html
import json
from pathlib import Path
from string import Template

ROOT = Path(__file__).parent
TPL = {p.stem: Template(p.read_text(encoding="utf-8")) for p in (ROOT / "templates").glob("*.html")}
DATA = json.loads((ROOT / "tasks.json").read_text(encoding="utf-8"))
COURSES, TASKS, THEORY = DATA["courses"], DATA["tasks"], DATA["theory"]
esc = html.escape

KEYS = {"grafika-inxhinierike": "tastet ← → ndërrojnë hapin, hapësira luan/ndal",
        "gjeometria-deskriptive": "tastet ← → ndërrojnë hapin, h hap rrafshet, v ndërron pamjen"}


def burimi(course):
    c = COURSES[course]
    return f"Burimi: {esc(c['book_cite'])}. {esc(DATA['credits'])}"


def animation_block(t):
    if t["animation"]:
        src = f"../animacione/{t['animation']}"
        steps = f"<small>vizatimi hap pas hapi, {t['steps']} hapa</small>" if t.get("steps") else ""
        return (f'<section class="animacioni"><h2>Animacioni {steps}</h2>'
                f'<div class="korniza"><iframe src="{src}" title="{esc(t["task"])} – {esc(t["title"])}, animacion hap pas hapi" '
                f'loading="lazy" allowfullscreen allow="fullscreen"></iframe></div>'
                f'<div class="pas-animacionit"><a class="hap-plote" href="{src}" target="_blank" rel="noopener">Hap në dritare të plotë ↗</a>'
                f'<p class="udhezim">Në projektor hape në dritare të plotë; {KEYS[t["course"]]}.</p></div></section>')
    below = "fletët e ndërtimit dhe faqet e librit" if t["sheets"] else "zgjidhjen nga libri"
    return ('<section class="animacioni"><h2>Animacioni</h2>'
            '<div class="vend-i-lire" role="note"><div class="ikona">▶</div>'
            '<p class="titulli">Animacioni për këtë detyrë është në përgatitje.</p>'
            f'<p class="nen">Ndërkohë shiko {below} më poshtë.</p></div></section>')


def figure_block(t):
    if not t["figure"]:
        return ""
    src = f"../{t['figure']}"
    return (f'<figure class="figura"><a href="{src}" target="_blank"><img src="{src}" alt="Figura e detyrës {esc(t["short"])} nga libri"></a>'
            f'<figcaption>Figura nga libri. Kliko për ta hapur më të madhe.</figcaption></figure>')


def sheets_block(t):
    if not t["sheets"]:
        return ""
    figs = "".join(f'<figure><a href="../{s["file"]}" target="_blank"><img src="../{s["file"]}" loading="lazy" alt="{esc(s["caption"])}"></a>'
                   f'<figcaption>{esc(s["caption"])}</figcaption></figure>' for s in t["sheets"])
    return (f'<section><h2>Fletët e ndërtimit <small>e dhëna → e gjetura</small></h2>'
            f'<p class="hyrja">Çdo fletë tregon majtas çka vizatohet drejtpërdrejt nga të dhënat dhe djathtas si gjenden qendrat e rakordeve dhe pikat e kontaktit.</p>'
            f'<div class="fletet">{figs}</div></section>')


def pages_block(t):
    if not t["pages"]:
        return ""
    book = COURSES[t["course"]]["book"]
    figs = []
    for p in t["pages"]:
        if isinstance(p, int):
            src, cap, alt = f"../libri/{book}/faqe-{p:02d}.jpg", f"Faqja {p} e librit", f"Faqja {p} e librit"
        else:
            src, cap, alt = f"../{p['file']}", p["caption"], p["caption"]
        figs.append(f'<figure><a href="{src}" target="_blank"><img src="{src}" loading="lazy" alt="{esc(alt)}"></a><figcaption>{esc(cap)}</figcaption></figure>')
    return f'<section><h2>Faqet e librit</h2><div class="faqet">{"".join(figs)}</div></section>'


def task_page(t, prev, nxt):
    c = COURSES[t["course"]]
    note = f'<p class="shenim">{esc(t["note"])}</p>' if t.get("note") else ""
    return TPL["faqe"].safe_substitute(
        course=esc(c["name"]), exercise=esc(t["exercise"]), task=esc(t["task"]), title=esc(t["title"]),
        kerkesa=esc(t["kerkesa"]), data=esc(t["data"]), note=note, number=esc(t["number"]),
        koka_class=" me-figure" if t["figure"] else "", figure=figure_block(t),
        animation=animation_block(t), sheets=sheets_block(t), pages=pages_block(t),
        prev=f'<a href="{prev["id"]}.html">← {esc(prev["task"])}</a>' if prev else "",
        nxt=f'<a href="{nxt["id"]}.html">{esc(nxt["task"])} →</a>' if nxt else "",
        burimi=burimi(t["course"]))


def course_page(course, mine):
    c = COURSES[course]
    sections = []
    for ex, meta in c["exercises"].items():
        rows = []
        with_fig = any(x["figure"] for x in mine if x["exercise"] == ex)
        for t in (x for x in mine if x["exercise"] == ex):
            status = (f'<span class="statusi ka">{t["steps"]} hapa</span>' if t["animation"]
                      else '<span class="statusi pa">në përgatitje</span>')
            fig = (f'<img class="fig" src="../{t["figure"]}" alt="" loading="lazy">' if t["figure"]
                   else ('<span class="fig"></span>' if with_fig else ""))
            rows.append(f'<li><a href="{t["id"]}.html"><span class="numri">{esc(t["short"])}</span>{fig}'
                        f'<span class="emri">{esc(t["title"])}</span>{status}</a></li>')
        where = f" Teksti i ushtrimit: faqja {meta['pages'][0]} e librit." if meta["pages"] else ""
        sections.append(f'<section class="ushtrimi" id="ushtrimi-{ex}"><h2>Ushtrimi {ex} <small>{esc(meta["title"])}</small></h2>'
                        f'<p class="permbledhje">{esc(meta["summary"])}{where}</p><ul class="lista{" me-figura" if with_fig else ""}">{"".join(rows)}</ul></section>')
    n_anim = sum(1 for t in mine if t["animation"])
    counts = f"{len(mine)} detyra, {n_anim} me animacion hap pas hapi; {len(mine) - n_anim} presin animacionin e tyre."
    teoria = ' <a href="teoria.html">Teoria: udhëzimi për detyrat</a>' if c["teoria"] else ""
    return TPL["lenda"].safe_substitute(
        course=esc(c["name"]), book_title=esc(c["book_title"]), intro=esc(c["intro"]), counts=counts,
        pdf=c["pdf"], pdf_size=c["pdf_size"], teoria_link=teoria, exercises="".join(sections),
        number=esc(c["number"]), burimi=burimi(course))


def theory_page(course):
    c = COURSES[course]
    chapters, toc = [], []
    for ch in THEORY:
        figs = "".join(f'<figure><a href="../libri/{c["book"]}/faqe-{p:02d}.jpg" target="_blank">'
                       f'<img src="../libri/{c["book"]}/faqe-{p:02d}.jpg" loading="lazy" alt="Faqja {p} e librit"></a>'
                       f'<figcaption>Faqja {p} e librit</figcaption></figure>' for p in ch["pages"])
        chapters.append(f'<section id="{ch["id"]}"><h2>{esc(ch["title"])}</h2><div class="faqet">{figs}</div></section>')
        toc.append(f'<a href="#{ch["id"]}">{esc(ch["title"])}</a>')
    return TPL["teoria"].safe_substitute(course=esc(c["name"]), contents=" · ".join(toc), chapters="".join(chapters),
                                         number=f'{c["number"]}.0', burimi=burimi(course))


def home_page():
    boxes = []
    for course, c in COURSES.items():
        mine = [t for t in TASKS if t["course"] == course]
        n_anim = sum(1 for t in mine if t["animation"])
        items = []
        for ex, meta in c["exercises"].items():
            ts = [t for t in mine if t["exercise"] == ex]
            a = sum(1 for t in ts if t["animation"])
            sa = f"{len(ts)} detyra, {a} me animacion" if a else f"{len(ts)} detyra"
            items.append(f'<li><a href="{course}/index.html#ushtrimi-{ex}">Ushtrimi {ex}: {esc(meta["title"])}</a><span class="sa">{sa}</span></li>')
        boxes.append(f'<section class="lenda"><h2><a href="{course}/index.html" style="text-decoration:none;color:inherit">{esc(c["name"])}</a></h2>'
                     f'<p class="numrat">{len(mine)} detyra, {n_anim} me animacion</p>'
                     f'<p>{esc(c["intro"])}</p>'
                     f'<ul>{"".join(items)}</ul>'
                     f'<p class="hap"><a class="hap-lenden" href="{course}/index.html">Hap lëndën</a></p></section>')
    cites = " ".join(f"{esc(c['book_cite'])}." for c in COURSES.values())
    return TPL["index"].safe_substitute(courses="".join(boxes), burimi=f"Burimi: {cites} {esc(DATA['credits'])}")


written = 0
for course in COURSES:
    mine = [t for t in TASKS if t["course"] == course]
    out = ROOT / course
    out.mkdir(exist_ok=True)
    for i, t in enumerate(mine):
        prev = mine[i - 1] if i else None
        nxt = mine[i + 1] if i + 1 < len(mine) else None
        (out / f"{t['id']}.html").write_text(task_page(t, prev, nxt), encoding="utf-8")
        written += 1
    (out / "index.html").write_text(course_page(course, mine), encoding="utf-8")
    if COURSES[course]["teoria"]:
        (out / "teoria.html").write_text(theory_page(course), encoding="utf-8")
(ROOT / "index.html").write_text(home_page(), encoding="utf-8")
print(f"{written} task pages written, {sum(1 for t in TASKS if t['animation'])} with animations; "
      f"{len(COURSES)} course pages, home and theory pages written.")
