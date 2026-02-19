#!/usr/bin/env python3
"""
MÍDIA GROSSA — Gerador Automático de Newsletter
Roda todo dia e publica em index.html
"""

import os
import json
import feedparser
import anthropic
from datetime import datetime, date
from zoneinfo import ZoneInfo

# ─── CONFIGURAÇÃO DOS FEEDS RSS ───────────────────────────────────────────────
FEEDS = {
    "politica": [
        "https://g1.globo.com/rss/g1/politica/",
        "https://agenciabrasil.ebc.com.br/rss/politica/feed.xml",
    ],
    "pop": [
        "https://g1.globo.com/rss/g1/pop-arte/",
        "https://www.uol.com.br/esporte/ultnot/ults4960.xml",
    ],
    "esportes": [
        "https://ge.globo.com/rss/ge/",
        "https://g1.globo.com/rss/g1/esportes/",
    ],
    "mercado": [
        "https://feeds.infomoney.com.br/infomoney/all",
        "https://agenciabrasil.ebc.com.br/rss/economia/feed.xml",
    ],
}

# ─── COLETA DE NOTÍCIAS ───────────────────────────────────────────────────────
def coletar_noticias(feeds: dict, max_por_feed: int = 8) -> dict:
    """Lê os RSS feeds e retorna um dicionário com as notícias por categoria."""
    noticias = {}

    for categoria, urls in feeds.items():
        itens = []
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:max_por_feed]:
                    titulo = entry.get("title", "").strip()
                    resumo = entry.get("summary", entry.get("description", "")).strip()
                    # Remove tags HTML do resumo
                    import re
                    resumo = re.sub(r"<[^>]+>", "", resumo)[:300]
                    if titulo:
                        itens.append({"titulo": titulo, "resumo": resumo})
            except Exception as e:
                print(f"  ⚠️  Erro ao ler feed {url}: {e}")

        noticias[categoria] = itens[:12]  # Máximo 12 por categoria
        print(f"  ✅ {categoria}: {len(noticias[categoria])} notícias coletadas")

    return noticias


# ─── GERAÇÃO VIA CLAUDE API ───────────────────────────────────────────────────
def gerar_html_com_claude(noticias: dict, hoje: str) -> str:
    """Envia as notícias pro Claude e recebe o HTML completo da newsletter."""

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    noticias_json = json.dumps(noticias, ensure_ascii=False, indent=2)

    prompt = f"""Você é o editor da newsletter "MÍDIA GROSSA" — uma newsletter brasileira com identidade visual de jornal tabloide, linguagem direta e moderna, com ênfase em futebol carioca.

Hoje é {hoje}.

Você recebeu as seguintes notícias coletadas de feeds RSS:

{noticias_json}

Sua tarefa: gerar uma página HTML COMPLETA e AUTOSSUFICIENTE da newsletter do dia.

REGRAS OBRIGATÓRIAS:
1. Use EXATAMENTE o mesmo HTML/CSS da newsletter modelo abaixo como base visual (mesmas fontes, cores, layout)
2. Selecione as 2-3 notícias mais relevantes de cada categoria
3. Reescreva os textos com linguagem jornalística brasileira — direto, sem enrolação
4. Para esportes, priorize futebol carioca (Flamengo, Fluminense, Vasco, Botafogo), depois futebol nacional, depois outros esportes
5. Para pop/internet, escolha o que seria mais "cronicamente online" e viral
6. Gere números fictícios plausíveis para o bloco de mercado SE não houver dados suficientes
7. Atualize o ticker "URGENTE" com os 3-4 fatos mais quentes do dia
8. O HTML deve ser 100% funcional standalone, com todas as fontes e estilos inline/embedded
9. Retorne APENAS o HTML, sem markdown, sem explicações, sem ```html

MODELO VISUAL (use exatamente este CSS/estrutura):

<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MÍDIA GROSSA — {hoje}</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Serif+Display:ital@0;1&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">
<style>
:root{{--ink:#0a0a0a;--paper:#f5f0e8;--accent:#d63b1f;--accent2:#1a4f8a;--muted:#7a7060;--rule:#c8bfaa;--highlight:#f0e030;}}
* {{margin:0;padding:0;box-sizing:border-box;}}
body {{background:var(--paper);color:var(--ink);font-family:'Space Mono',monospace;font-size:14px;line-height:1.6;}}
.masthead {{background:var(--ink);color:var(--paper);text-align:center;padding:12px 24px 0;border-bottom:4px solid var(--accent);}}
.top-bar {{display:flex;justify-content:space-between;align-items:center;font-size:10px;letter-spacing:0.12em;text-transform:uppercase;opacity:0.6;margin-bottom:8px;font-family:'Syne',sans-serif;}}
.logo {{font-family:'Bebas Neue',sans-serif;font-size:clamp(64px,12vw,120px);letter-spacing:-0.02em;line-height:0.85;color:var(--paper);display:inline-block;}}
.logo span {{color:var(--accent);}}
.tagline {{font-family:'DM Serif Display',serif;font-style:italic;font-size:13px;opacity:0.7;padding:8px 0 16px;}}
.nav-strip {{display:flex;justify-content:center;border-top:1px solid rgba(255,255,255,0.15);margin-top:4px;}}
.nav-item {{padding:8px 20px;font-family:'Syne',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:var(--paper);opacity:0.55;border-right:1px solid rgba(255,255,255,0.1);text-decoration:none;}}
.nav-item.active {{opacity:1;color:var(--highlight);}}
.breaking {{background:var(--accent);color:white;padding:10px 24px;display:flex;align-items:center;gap:16px;overflow:hidden;}}
.breaking-label {{font-family:'Bebas Neue',sans-serif;font-size:18px;flex-shrink:0;background:white;color:var(--accent);padding:2px 10px;}}
.breaking-text {{font-family:'Syne',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;white-space:nowrap;animation:ticker 22s linear infinite;}}
@keyframes ticker {{0%{{transform:translateX(0)}}100%{{transform:translateX(-50%)}}}}
.container {{max-width:920px;margin:0 auto;padding:0 20px;}}
.section-header {{display:flex;align-items:center;gap:12px;margin:40px 0 20px;}}
.section-label {{font-family:'Bebas Neue',sans-serif;font-size:36px;letter-spacing:0.04em;line-height:1;flex-shrink:0;}}
.section-line {{flex:1;height:2px;background:var(--ink);}}
.section-number {{font-family:'Space Mono',monospace;font-size:10px;color:var(--muted);flex-shrink:0;}}
.lead-story {{border-top:4px solid var(--ink);border-bottom:1px solid var(--rule);padding:32px 0 24px;display:grid;grid-template-columns:1fr 260px;gap:40px;align-items:start;}}
.lead-kicker {{font-family:'Syne',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:var(--accent);margin-bottom:10px;}}
.lead-headline {{font-family:'Bebas Neue',sans-serif;font-size:clamp(42px,6vw,72px);letter-spacing:-0.01em;line-height:0.9;margin-bottom:16px;}}
.lead-headline em {{font-style:normal;color:var(--accent);display:block;}}
.lead-dek {{font-family:'DM Serif Display',serif;font-size:17px;line-height:1.5;color:#2a2620;margin-bottom:16px;}}
.lead-body {{font-size:13px;line-height:1.7;color:#3a342c;}}
.lead-sidebar {{border-left:2px solid var(--rule);padding-left:24px;}}
.sidebar-stat {{margin-bottom:24px;padding-bottom:20px;border-bottom:1px dotted var(--rule);}}
.sidebar-stat:last-child {{border-bottom:none;}}
.stat-number {{font-family:'Bebas Neue',sans-serif;font-size:48px;line-height:1;color:var(--accent);}}
.stat-label {{font-family:'Syne',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-top:2px;}}
.stat-desc {{font-size:11px;line-height:1.5;color:var(--muted);margin-top:6px;}}
.two-col {{display:grid;grid-template-columns:1fr 1fr;gap:32px;border-top:1px solid var(--rule);padding-top:24px;margin-bottom:8px;margin-top:24px;}}
.three-col {{display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;border-top:1px solid var(--rule);padding-top:24px;margin-bottom:8px;}}
.story-card + .story-card {{border-left:1px solid var(--rule);padding-left:24px;}}
.card-kicker {{font-family:'Syne',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:var(--muted);margin-bottom:8px;}}
.card-headline {{font-family:'DM Serif Display',serif;font-size:20px;line-height:1.2;margin-bottom:10px;}}
.card-headline em {{font-style:italic;color:var(--accent);}}
.card-body {{font-size:12px;line-height:1.65;color:#3a342c;}}
.card-tag {{display:inline-block;margin-top:10px;font-family:'Syne',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;background:var(--ink);color:var(--paper);padding:3px 8px;}}
.pullquote {{border-left:5px solid var(--accent);margin:28px 0;padding:16px 24px;background:rgba(214,59,31,0.04);}}
.pullquote p {{font-family:'DM Serif Display',serif;font-style:italic;font-size:22px;line-height:1.35;margin-bottom:8px;}}
.pullquote cite {{font-family:'Syne',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);font-style:normal;}}
.market-block {{background:var(--ink);color:var(--paper);padding:28px 32px;margin:8px 0;}}
.market-title {{font-family:'Bebas Neue',sans-serif;font-size:28px;letter-spacing:0.06em;margin-bottom:20px;color:var(--highlight);}}
.market-grid {{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border-top:1px solid rgba(255,255,255,0.15);border-left:1px solid rgba(255,255,255,0.15);}}
.market-item {{padding:16px 20px;border-right:1px solid rgba(255,255,255,0.15);border-bottom:1px solid rgba(255,255,255,0.15);}}
.market-name {{font-family:'Syne',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;opacity:0.5;margin-bottom:4px;}}
.market-value {{font-family:'Bebas Neue',sans-serif;font-size:32px;letter-spacing:-0.01em;line-height:1;}}
.market-change {{font-family:'Space Mono',monospace;font-size:11px;margin-top:4px;font-weight:700;}}
.up{{color:#4ade80;}}.down{{color:#f87171;}}.neutral{{color:rgba(255,255,255,0.5);}}
.market-note {{font-size:11px;line-height:1.6;opacity:0.6;margin-top:16px;border-top:1px solid rgba(255,255,255,0.1);padding-top:12px;font-style:italic;}}
.divider {{display:flex;align-items:center;gap:16px;margin:32px 0;color:var(--muted);font-family:'Syne',sans-serif;font-size:10px;letter-spacing:0.15em;text-transform:uppercase;}}
.divider::before,.divider::after {{content:'';flex:1;height:1px;background:var(--rule);}}
.pop-grid {{display:grid;grid-template-columns:1fr 1fr;gap:0;border:2px solid var(--ink);margin:8px 0;}}
.pop-item {{padding:20px 24px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);position:relative;}}
.pop-item:nth-child(2n){{border-right:none;}}.pop-item:nth-last-child(-n+2){{border-bottom:none;}}
.pop-number {{font-family:'Bebas Neue',sans-serif;font-size:64px;line-height:1;color:rgba(0,0,0,0.06);position:absolute;top:8px;right:12px;}}
.pop-emoji {{font-size:22px;margin-bottom:8px;display:block;}}
.pop-headline {{font-family:'DM Serif Display',serif;font-size:16px;line-height:1.3;margin-bottom:6px;}}
.pop-body {{font-size:11px;line-height:1.6;color:var(--muted);}}
.pop-viral {{display:inline-flex;align-items:center;gap:4px;margin-top:8px;background:var(--highlight);color:var(--ink);font-family:'Syne',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:2px 7px;}}
hr.section-divider {{border:none;border-top:3px double var(--rule);margin:40px 0;}}
footer {{background:var(--ink);color:rgba(245,240,232,0.4);padding:32px 24px 24px;margin-top:48px;text-align:center;}}
.footer-logo {{font-family:'Bebas Neue',sans-serif;font-size:32px;color:var(--paper);letter-spacing:0.06em;margin-bottom:8px;}}
.footer-logo span{{color:var(--accent);}}
.footer-text {{font-family:'Syne',sans-serif;font-size:10px;letter-spacing:0.1em;text-transform:uppercase;line-height:2;}}
@media(max-width:680px){{.lead-story{{grid-template-columns:1fr}}.lead-sidebar{{display:none}}.two-col,.three-col,.pop-grid{{grid-template-columns:1fr}}.story-card+.story-card{{border-left:none;border-top:1px solid var(--rule);padding-left:0;padding-top:20px}}.market-grid{{grid-template-columns:1fr 1fr}}}}
</style>
</head>
<body>
<!-- AQUI VOCÊ GERA TODO O CONTEÚDO SEGUINDO EXATAMENTE ESSA ESTRUTURA -->
<!-- masthead → breaking ticker → seção política → seção pop → seção esportes → seção mercado → footer -->
</body>
</html>

Agora gere a newsletter COMPLETA de {hoje} com as notícias fornecidas. Retorne APENAS o HTML final."""

    print("  🤖 Enviando para Claude API...")
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
    )

    html = response.content[0].text.strip()

    # Remove blocos markdown caso Claude os inclua
    if html.startswith("```"):
        html = html.split("\n", 1)[1]
    if html.endswith("```"):
        html = html.rsplit("```", 1)[0]

    return html.strip()


# ─── SALVAR ARQUIVOS ──────────────────────────────────────────────────────────
def salvar(html: str, hoje_str: str):
    """Salva index.html (sempre atual) e uma cópia com a data."""
    # Arquivo principal (o que o GitHub Pages serve)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    # Arquivo de arquivo histórico
    os.makedirs("edicoes", exist_ok=True)
    with open(f"edicoes/{hoje_str}.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  💾 Salvo: index.html e edicoes/{hoje_str}.html")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    tz = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(tz)
    hoje_str = agora.strftime("%Y-%m-%d")
    hoje_fmt = agora.strftime("%A, %d de %B de %Y").capitalize()

    print(f"\n📰 MÍDIA GROSSA — Gerando edição de {hoje_fmt}\n")

    print("📡 Coletando notícias dos feeds RSS...")
    noticias = coletar_noticias(FEEDS)

    print("\n✍️  Gerando HTML com Claude...")
    html = gerar_html_com_claude(noticias, hoje_fmt)

    print("\n💾 Salvando arquivos...")
    salvar(html, hoje_str)

    print(f"\n✅ Edição de {hoje_fmt} gerada com sucesso!\n")


if __name__ == "__main__":
    main()
