# -*- coding: utf-8 -*-
"""Reconstroi o feed RSS do COMPASSO CAPITAL.

  python scripts/publicar_feed.py                      # so reconstroi
  python scripts/publicar_feed.py --acrescentar N ...  # registra um episodio

O feed e sempre reconstruido inteiro a partir de scripts/episodios.json, para nunca
depender de edicao manual de XML.
"""
import json, pathlib, re, sys
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from xml.sax.saxutils import escape

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ESTADO = RAIZ / "scripts" / "episodios.json"
FEED = RAIZ / "feed.xml"

SITE = "https://compasso.capital"
PAGES = "https://galiciaeducacao.github.io/compasso-podcast"
RELEASES = "https://github.com/galiciaeducacao/compasso-podcast/releases/download"
TITULO, AUTOR = "COMPASSO CAPITAL", "COMPASSO"
EMAIL = "contato@compasso.capital"
CAPA = f"{PAGES}/capa.png"
DESCRICAO = ("O podcast que traduz os interesses nas entrelinhas das notícias. "
             "Todos os dias, às 7 da manhã, Davi e Helena abrem cinco notícias que a imprensa "
             "brasileira não conta direito, em quatro tempos: o que aconteceu, em que jogo isso "
             "se encaixa, quem ganha e quem perde, e o que pode vir depois. "
             "Porque no jogo do excedente, ninguém assiste de fora. "
             "Análises completas em compasso.capital.")
FUSO = timezone(timedelta(hours=-3))


def carregar():
    return json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {"episodios": []}


def acrescentar(numero, titulo, descricao, duracao, tamanho, data_iso):
    d = carregar()
    arquivo = f"compasso-capital-{numero:04d}.mp3"
    ep = {"numero": numero, "titulo": titulo, "descricao": descricao,
          "notas": ("<p>Todas as análises completas, com fontes, em "
                    "<a href='https://compasso.capital'>compasso.capital</a>.</p>"),
          "arquivo": arquivo, "url": f"{RELEASES}/ep{numero:04d}/{arquivo}",
          "tamanho": int(tamanho), "duracao": duracao, "data": data_iso,
          "guid": f"compasso-capital-ep{numero:04d}"}
    d["episodios"] = [e for e in d["episodios"] if e["numero"] != numero] + [ep]
    d["episodios"].sort(key=lambda e: e["numero"], reverse=True)
    ESTADO.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return ep


def gerar():
    eps = carregar()["episodios"]
    itens = []
    for e in eps:
        dt = datetime.fromisoformat(e["data"]).replace(tzinfo=FUSO)
        itens.append(f"""    <item>
      <title>{escape(e['titulo'])}</title>
      <description>{escape(e['descricao'])}</description>
      <itunes:summary>{escape(e['descricao'])}</itunes:summary>
      <content:encoded><![CDATA[{e.get('notas','')}]]></content:encoded>
      <enclosure url="{e['url']}" length="{e['tamanho']}" type="audio/mpeg"/>
      <guid isPermaLink="false">{e['guid']}</guid>
      <pubDate>{format_datetime(dt)}</pubDate>
      <itunes:duration>{e['duracao']}</itunes:duration>
      <itunes:episode>{e['numero']}</itunes:episode>
      <itunes:episodeType>full</itunes:episodeType>
      <itunes:explicit>false</itunes:explicit>
      <link>{PAGES}/</link>
    </item>""")

    FEED.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{TITULO}</title>
    <link>{SITE}</link>
    <language>pt-BR</language>
    <copyright>© COMPASSO CAPITAL</copyright>
    <description>{escape(DESCRICAO)}</description>
    <itunes:summary>{escape(DESCRICAO)}</itunes:summary>
    <itunes:author>{AUTOR}</itunes:author>
    <itunes:type>episodic</itunes:type>
    <itunes:explicit>false</itunes:explicit>
    <itunes:image href="{CAPA}"/>
    <image><url>{CAPA}</url><title>{TITULO}</title><link>{SITE}</link></image>
    <itunes:owner><itunes:name>{AUTOR}</itunes:name><itunes:email>{EMAIL}</itunes:email></itunes:owner>
    <itunes:category text="News"><itunes:category text="Business News"/></itunes:category>
    <itunes:category text="Business"><itunes:category text="Investing"/></itunes:category>
    <atom:link href="{PAGES}/feed.xml" rel="self" type="application/rss+xml"/>
    <lastBuildDate>{format_datetime(datetime.now(FUSO))}</lastBuildDate>
{chr(10).join(itens)}
  </channel>
</rss>
""", encoding="utf-8")
    return len(eps)


if __name__ == "__main__":
    if "--acrescentar" in sys.argv:
        i = sys.argv.index("--acrescentar")
        acrescentar(int(sys.argv[i+1]), sys.argv[i+2], sys.argv[i+3],
                    sys.argv[i+4], sys.argv[i+5], sys.argv[i+6])
        print(f"episodio {sys.argv[i+1]} registrado")
    print(f"feed com {gerar()} episodio(s)")
