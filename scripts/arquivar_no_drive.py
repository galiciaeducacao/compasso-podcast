# -*- coding: utf-8 -*-
"""Traz para o Drive todo episodio que ainda nao esta la.

  python scripts/arquivar_no_drive.py

Existe porque os episodios gerados no servidor do GitHub NAO chegam ao Drive sozinhos:
o runner nao enxerga o Drive do Paulo. Os episodios 1 e 2 estavam la so porque foram
gerados na maquina local; o 3 e o 4 nasceram na nuvem e sumiram do arquivo da casa.

Roda nesta maquina, e so aqui pode rodar. E idempotente: baixa apenas o que falta, e
pode ser chamado quantas vezes quiser.

Para cada episodio monta a pasta no padrao da casa:
  EP0N_<data>/COMPASSO_CAPITAL_EP0N_<data>.mp3
  EP0N_<data>/COMPASSO_CAPITAL_EP0N_roteiro.md
  EP0N_<data>/COMPASSO_CAPITAL_EP0N_transcricao.txt   (com marcacao de tempo)
"""
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request
import uuid

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DRIVE = pathlib.Path(r"J:\Meu Drive\Podcast Compasso Capital")
REPO = "galiciaeducacao/compasso-podcast"


def chave_elevenlabs():
    cofre = pathlib.Path(r"H:\Meu Drive\_Claude-Privado\_credenciais\elevenlabs.json")
    if not cofre.exists():
        return ""
    return json.loads(cofre.read_text(encoding="utf-8-sig")).get("api_key", "")


def transcrever(mp3, destino, key):
    """transcricao com marcacao de tempo, que e o que permite dizer 'erro aos 2min10'"""
    lim = "----" + uuid.uuid4().hex
    corpo = b""
    for c, v in (("model_id", "scribe_v1"), ("language_code", "por"),
                 ("timestamps_granularity", "word")):
        corpo += f"--{lim}\r\nContent-Disposition: form-data; name=\"{c}\"\r\n\r\n{v}\r\n".encode()
    corpo += (f"--{lim}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.mp3\"\r\n"
              f"Content-Type: audio/mpeg\r\n\r\n").encode() + mp3.read_bytes() \
             + f"\r\n--{lim}--\r\n".encode()
    r = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", data=corpo,
        headers={"xi-api-key": key, "Content-Type": f"multipart/form-data; boundary={lim}"},
        method="POST")
    with urllib.request.urlopen(r, timeout=900) as resp:
        dados = json.loads(resp.read())
    palavras = [w for w in dados.get("words", []) if w.get("type") == "word"]
    linhas, atual, inicio = [], [], None
    for w in palavras:
        if inicio is None:
            inicio = float(w["start"])
        atual.append(w["text"])
        if w["text"].rstrip().endswith((".", "!", "?")) or len(atual) >= 20:
            linhas.append("[%02d:%02d] %s" % (inicio // 60, inicio % 60, " ".join(atual)))
            atual, inicio = [], None
    if atual:
        linhas.append("[%02d:%02d] %s" % (inicio // 60, inicio % 60, " ".join(atual)))
    destino.write_text("\n".join(linhas), encoding="utf-8")
    return len(linhas)


def main():
    if not DRIVE.is_dir():
        sys.exit(f"o Drive nao esta acessivel em {DRIVE}")
    episodios = json.loads((RAIZ / "scripts" / "episodios.json")
                           .read_text(encoding="utf-8"))["episodios"]
    key = chave_elevenlabs()
    novos = 0

    for e in episodios:
        num, data = e["numero"], e["data"][:10]
        # reaproveita a pasta que ja existe para esse episodio, mesmo com outra data no
        # nome: a do episodio 1 foi criada com a data da GRAVACAO e as demais com a do
        # AR. Criar outra so porque o nome difere gera pasta duplicada, que foi o que
        # aconteceu na primeira rodada.
        existentes = sorted(DRIVE.glob(f"EP{num:02d}_*"))
        pasta = existentes[0] if existentes else DRIVE / f"EP{num:02d}_{data}"
        mp3 = pasta / f"COMPASSO_CAPITAL_EP{num:02d}_{data}.mp3"
        if mp3.exists() and mp3.stat().st_size == e["tamanho"]:
            print(f"  episodio {num}: ja arquivado")
            continue

        pasta.mkdir(exist_ok=True)
        print(f"  episodio {num}: baixando {e['tamanho']:,} bytes...")
        # o Drive e sincronizado: o tamanho lido logo apos escrever pode vir menor do
        # que o final, e a primeira versao deste script acusou download truncado que
        # estava intacto. Confere com paciencia antes de reclamar.
        for tentativa in range(3):
            urllib.request.urlretrieve(e["url"], mp3)
            for _ in range(10):
                if mp3.stat().st_size == e["tamanho"]:
                    break
                time.sleep(1)
            if mp3.stat().st_size == e["tamanho"]:
                break
            print(f"    tentativa {tentativa+1}: baixou {mp3.stat().st_size:,} de "
                  f"{e['tamanho']:,}, refazendo")
        else:
            print(f"    ::error:: nao consegui baixar o episodio {num} inteiro")
            continue

        roteiro = RAIZ / "roteiros" / f"{data}.md"
        if roteiro.exists():
            (pasta / f"COMPASSO_CAPITAL_EP{num:02d}_roteiro.md").write_text(
                roteiro.read_text(encoding="utf-8"), encoding="utf-8")

        alvo = pasta / f"COMPASSO_CAPITAL_EP{num:02d}_transcricao.txt"
        if key and not alvo.exists():
            n = transcrever(mp3, alvo, key)
            print(f"    transcricao com tempo: {n} linhas")
        print(f"    arquivado em {pasta.name}")
        novos += 1

    print(f"\n{novos} episodio(s) trazido(s) para o Drive." if novos
          else "\nnada faltando: o Drive ja tem todos os episodios.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
