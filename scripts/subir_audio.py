# -*- coding: utf-8 -*-
"""Poe o mp3 do episodio no R2, que e de onde o ouvinte toca.

  python scripts/subir_audio.py <arquivo.mp3> [nome-no-balde.mp3]

POR QUE ISSO EXISTE. Ate 01/09/2026 o feed apontava para o release do GitHub, e a
Apple recusava tocar. Testado na origem, o release responde:

    Content-Type: application/octet-stream
    Content-Disposition: attachment; filename=compasso-capital-0004.mp3

Isso e o servidor dizendo "baixe este arquivo", nao "toque este audio", e o player
obedece. O Spotify passava porque baixa e re-hospeda; a Apple toca da origem. Alem
disso a URL final do release e assinada e expira em cerca de uma hora.

O release continua sendo gerado pelo workflow, como backup e historico. O que muda e
so o endereco publico: audio.compasso.capital, servido como audio/mpeg de verdade.

CREDENCIAIS: quatro variaveis de ambiente, nunca em arquivo.
  R2_ACCOUNT_ID          o identificador da conta Cloudflare
  R2_ACCESS_KEY_ID       do token de API do R2
  R2_SECRET_ACCESS_KEY   idem
  R2_BUCKET              o nome do balde (ex.: compasso-audio)
"""
import mimetypes
import os
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def cliente():
    """conexao com o R2 pela interface S3, que e o que ele fala"""
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        sys.exit("falta o boto3: pip install boto3")
    faltando = [v for v in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID",
                            "R2_SECRET_ACCESS_KEY", "R2_BUCKET")
                if not os.environ.get(v)]
    if faltando:
        sys.exit("faltam variaveis de ambiente: " + ", ".join(faltando))
    conta = os.environ["R2_ACCOUNT_ID"]
    return boto3.client(
        "s3",
        endpoint_url=f"https://{conta}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        # o R2 so aceita esta regiao; qualquer outra e recusada na assinatura
        region_name="auto",
        config=Config(signature_version="s3v4"),
    ), os.environ["R2_BUCKET"]


def subir(caminho, nome=None):
    """sobe um arquivo e devolve o tamanho confirmado pelo servidor"""
    s3, balde = cliente()
    caminho = pathlib.Path(caminho)
    nome = nome or caminho.name
    tipo = mimetypes.guess_type(nome)[0] or "application/octet-stream"

    # O ContentType E O PONTO DA MUDANCA. Sem ele o R2 tambem entregaria
    # octet-stream, e teriamos trocado de servidor sem resolver nada.
    # ContentDisposition inline diz ao player para tocar, nao baixar.
    s3.upload_file(str(caminho), balde, nome,
                   ExtraArgs={"ContentType": tipo,
                              "ContentDisposition": "inline",
                              "CacheControl": "public, max-age=31536000, immutable"})

    # confere do outro lado: subida que "deu certo" e chegou truncada ja aconteceu
    # neste projeto com o arquivamento no Drive, e custou um episodio sem copia
    cabeca = s3.head_object(Bucket=balde, Key=nome)
    local = caminho.stat().st_size
    if cabeca["ContentLength"] != local:
        sys.exit(f"::error::subiu {cabeca['ContentLength']} de {local} bytes em {nome}")
    print(f"  {nome}: {local:,} bytes, {cabeca['ContentType']}")
    return local


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    subir(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
