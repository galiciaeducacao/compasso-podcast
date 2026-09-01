# -*- coding: utf-8 -*-
"""Mantem o balde do audio dentro da faixa gratuita do R2.

  python scripts/limpar_r2.py --conferir   # so mostra o que faria
  python scripts/limpar_r2.py              # apaga de verdade

A CONTA. A faixa gratuita do R2 e 10 GB-mes de armazenamento, 1 milhao de operacoes de
escrita e 10 milhoes de leitura por mes, e a saida de dados e gratuita SEMPRE
(developers.cloudflare.com/r2/pricing, conferido em 01/09/2026). Como a saida nao custa,
o unico jeito de o R2 comecar a cobrar e o balde encher. Um episodio pesa ~21 MB e sai um
por dia: ~640 MB por mes, e o balde encostaria nos 10 GB por volta do decimo sexto mes.
Ou seja, sem esta rotina o programa passa a pagar em algum momento de 2027. Com ela, o
balde estaciona em ~3,8 GB e nao passa nunca.

O QUE ELA APAGA, E O QUE NAO SE PERDE. Fica servido no R2 a JANELA de episodios mais
recentes. O que sai continua existindo como release do GitHub, que e o arquivo frio do
programa e nao conta em cota nenhuma. Por isso o episodio so e apagado do R2 DEPOIS de
confirmar, por HTTP, que o release dele ainda responde. Sem essa confirmacao, nao apaga.

O EPISODIO APAGADO SAI DO FEED JUNTO. Tem que sair: enclosure apontando para arquivo que
nao existe mais quebra o episodio em todos os tocadores, e isso e pior que um episodio
ausente. O registro dele continua em episodios.json, marcado como arquivado, o que
preserva a numeracao e o historico. Programa diario de noticia nao perde nada com isso:
episodio de seis meses atras nao tem ouvinte.
"""
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

import publicar_feed
from subir_audio import cliente

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ESTADO = RAIZ / "scripts" / "episodios.json"
RELEASES = "https://github.com/galiciaeducacao/compasso-podcast/releases/download"

# Quantos episodios ficam servidos. 180 sao seis meses, ~3,8 GB: pouco mais de um terco
# da faixa gratuita, com folga para o episodio engordar sem susto.
JANELA = int(os.environ.get("COMPASSO_JANELA", "180"))

# Teto de seguranca. A janela e contada em EPISODIOS e a cota e cobrada em BYTES: se um
# dia o episodio dobrar de tamanho, a janela sozinha nao perceberia. Entao ela encolhe
# ate caber aqui.
ALVO_BYTES = int(os.environ.get("COMPASSO_ALVO_BYTES", str(8 * 10**9)))

GRATUITO = 10 * 10**9


def uso(s3, balde):
    """(bytes guardados, quantidade de objetos) no balde inteiro"""
    total, quantos, token = 0, 0, None
    while True:
        kw = {"Bucket": balde}
        if token:
            kw["ContinuationToken"] = token
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            total += o["Size"]
            quantos += 1
        if not r.get("IsTruncated"):
            return total, quantos
        token = r.get("NextContinuationToken")


def release_responde(url):
    """O arquivo frio existe mesmo? Sem isto, apagar do R2 e perder o episodio."""
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "compasso-limpeza"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status == 200
    except urllib.error.HTTPError as e:
        return e.code == 200
    except Exception:
        return False


def main():
    conferir = "--conferir" in sys.argv

    if not os.environ.get("R2_ACCOUNT_ID"):
        # Faxineiro semanal: sem R2 configurado nao ha o que limpar, e isso nao e falha.
        # Sair com erro aqui encheria a caixa de e-mail toda semana sem motivo.
        print("::notice::Sem credencial do R2. Nada a limpar.")
        return 0

    s3, balde = cliente()
    guardado, quantos = uso(s3, balde)
    print(f"balde hoje: {quantos} arquivo(s), {guardado / 10**9:.2f} GB "
          f"({guardado / GRATUITO * 100:.0f}% da faixa gratuita)")

    d = json.loads(ESTADO.read_text(encoding="utf-8"))
    vivos = [e for e in d["episodios"]
             if not e.get("arquivado") and e["url"].startswith("https://audio.")]
    vivos.sort(key=lambda e: e["numero"], reverse=True)

    janela = min(JANELA, len(vivos))
    while janela > 1 and sum(e["tamanho"] for e in vivos[:janela]) > ALVO_BYTES:
        janela -= 1

    sair = vivos[janela:]
    if not sair:
        print(f"{len(vivos)} episodio(s) servido(s), janela de {JANELA}. "
              "Nada a apagar: o balde ainda nao encheu.")
        return 0

    print(f"\nmantendo os {janela} mais recentes; {len(sair)} sai(em) do balde:")
    for e in sair:
        print(f"  ep{e['numero']:04d}  {e['data'][:10]}  {e['tamanho']:,} bytes")
    if conferir:
        print("\n(--conferir: nada foi apagado)")
        return 0

    apagados, liberados = 0, 0
    for e in sair:
        frio = f"{RELEASES}/ep{e['numero']:04d}/{e['arquivo']}"
        if not release_responde(frio):
            print(f"::warning::ep{e['numero']:04d} NAO apagado: o release {frio} nao "
                  "respondeu 200. Sem arquivo frio, apagar seria perder o episodio.")
            continue
        s3.delete_object(Bucket=balde, Key=e["arquivo"])
        e["arquivado"] = True
        e["url_arquivo"] = frio
        apagados += 1
        liberados += e["tamanho"]
        print(f"  ep{e['numero']:04d} apagado do R2 (release confirmado)")

    ESTADO.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    itens = publicar_feed.gerar()

    sobra, _ = uso(s3, balde)
    print(f"\n{apagados} episodio(s) apagado(s), {liberados / 10**9:.2f} GB liberado(s).")
    print(f"balde agora: {sobra / 10**9:.2f} GB ({sobra / GRATUITO * 100:.0f}% do gratuito).")
    print(f"feed com {itens} episodio(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
