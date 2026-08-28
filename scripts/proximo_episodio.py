# -*- coding: utf-8 -*-
"""Diz qual episodio gravar, sem depender da hora em que o workflow rodou.

  python scripts/proximo_episodio.py

O agendador do GitHub e best effort: em 27/08 o disparo das 18h saiu as 2h da manha,
oito horas atrasado. Como o workflow calculava o alvo com `date -d "+1 day"`, o atraso
atravessou a meia-noite e "amanha" virou o dia errado. Naquele dia deu sorte e nao
achou roteiro; se tivesse rodado no horario teria gravado um episodio duplicado.

Entao o alvo nao se calcula pelo relogio. Ele se DEDUZ do estado:

  o primeiro dia, de hoje em diante, que tem roteiro aprovado
  e ainda nao tem episodio publicado nem gravado

Assim um disparo atrasado, repetido ou fora de hora acerta o mesmo alvo, e disparo
duplicado nao gera episodio duplicado. Nao imprime nada se nao houver o que fazer.
"""
import datetime as dt
import json
import os
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def main():
    hoje = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).date()

    ja = json.loads((RAIZ / "scripts" / "episodios.json").read_text(encoding="utf-8"))
    publicados = {e["data"][:10] for e in ja["episodios"]}
    numeros = [e["numero"] for e in ja["episodios"]]
    gravados = {p.stem for p in (RAIZ / "pendentes").glob("*.json")} \
        if (RAIZ / "pendentes").exists() else set()

    datas = sorted(p.stem for p in (RAIZ / "roteiros").glob("*.md")
                   if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.stem))

    for d in datas:
        if d in publicados or d in gravados:
            continue                      # ja saiu, ou ja esta gravado esperando as 7h
        if dt.date.fromisoformat(d) < hoje:
            continue                      # roteiro vencido: nao se grava episodio de ontem
        numero = max(numeros + [0]) + 1
        saida = os.environ.get("GITHUB_OUTPUT")
        linhas = f"tem=sim\ndata={d}\nnumero={numero}\n"
        if saida:
            with open(saida, "a", encoding="utf-8") as fh:
                fh.write(linhas)
        print(f"Alvo: episodio {numero} para {d}")
        return 0

    saida = os.environ.get("GITHUB_OUTPUT")
    if saida:
        with open(saida, "a", encoding="utf-8") as fh:
            fh.write("tem=nao\n")
    print("Nenhum roteiro aprovado aguardando gravacao. Nada a fazer (isto nao e erro).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
