"""Gera langs.svg com as linguagens de todos os repositórios do dono (privados incluídos), sem forks."""
import json
import os
import urllib.request
from xml.sax.saxutils import escape

TOKEN = os.environ["GH_TOKEN"]
SKIP = {os.environ.get("GH_USER", "")}
TOP = 8
COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Java": "#b07219", "Go": "#00ADD8",
    "C#": "#178600", "HTML": "#e34c26", "CSS": "#663399", "Python": "#3572A5", "Shell": "#89e051",
    "Kotlin": "#A97BFF", "SCSS": "#c6538c", "Dockerfile": "#384d54", "PLpgSQL": "#336790",
}


def get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}",
                                               "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def totals():
    sums, page = {}, 1
    while True:
        repos = get(f"https://api.github.com/user/repos?affiliation=owner&per_page=100&page={page}")
        if not repos:
            return sums
        for repo in repos:
            if repo["fork"] or repo["archived"] or repo["name"] in SKIP:
                continue
            for lang, size in get(repo["languages_url"]).items():
                sums[lang] = sums.get(lang, 0) + size
        page += 1


def svg(sums):
    top = sorted(sums.items(), key=lambda kv: -kv[1])[:TOP]
    total = sum(v for _, v in top) or 1
    w, bar_w = 350, 300
    rows = (len(top) + 1) // 2
    h = 75 + rows * 24
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
           '<style>.t{font:600 16px "Segoe UI",Ubuntu,sans-serif;fill:#2F81F7}'
           '.l{font:400 12px "Segoe UI",Ubuntu,sans-serif;fill:#8B949E}</style>',
           '<text x="25" y="32" class="t">Linguagens mais usadas</text>',
           '<clipPath id="r"><rect x="25" y="47" width="300" height="8" rx="4"/></clipPath><g clip-path="url(#r)">']
    x = 25.0
    for lang, size in top:
        seg = bar_w * size / total
        out.append(f'<rect x="{x:.2f}" y="47" width="{seg + 0.5:.2f}" height="8" fill="{COLORS.get(lang, "#8B949E")}"/>')
        x += seg
    out.append("</g>")
    for i, (lang, size) in enumerate(top):
        cx = 25 + (i % 2) * 160
        cy = 80 + (i // 2) * 24
        out.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{COLORS.get(lang, "#8B949E")}"/>')
        out.append(f'<text x="{cx + 16}" y="{cy}" class="l">{escape(lang)} {100 * size / total:.2f}%</text>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    print(svg(totals()))
