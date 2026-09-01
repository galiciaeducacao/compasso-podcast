# -*- coding: utf-8 -*-
"""Leva os episodios que ja estao no ar do release do GitHub para o R2.

  python scripts/migrar_audio_para_r2.py            # mostra o que faria
  python scripts/migrar_audio_para_r2.py --aplicar  # baixa, sobe e reescreve o feed

Os cinco primeiros episodios foram publicados apontando para o release do GitHub, que
a Apple recusa tocar (ver scripts/subir_audio.py para o diagnostico). Este script os
move para o endereco novo.

O GUID NAO MUDA, e e isso que segura tudo: para a Apple e para o Spotify, o episodio
continua sendo o mesmo, so que servido de outro lugar. Mudar o GUID criaria episodios
duplicados no aparelho de quem ja assina.

E idempotente: episodio que ja esta no R2 com o tamanho certo e pulado.
"""
import json
import pathlib
import subprocess
import sys
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ESTADO = RAIZ / "scripts" / "episodios.json"
TMP = RAIZ / "_tmp_migracao"
AUDIO = "https://audio.compasso.capital"

sys.path.insert(0, str(RAIZ / "scripts"))


def main():
    aplicar = "--aplicar" in sys.argv
    d = json.loads(ESTADO.read_text(encoding="utf-8"))
    eps = d["episodios"]
    pendentes = [e for e in eps if not e["url"].startswith(AUDIO)]

    if not pendentes:
        print("nada a migrar: todos os episodios ja apontam para o R2")
        return 0

    print(f"{len(pendentes)} episodio(s) para migrar:")
    for e in pendentes:
        print(f"  {e['numero']:>2}  {e['arquivo']}  {e['tamanho']:,} bytes")
    if not aplicar:
        print("\nMODO SECO. Nada foi alterado. Use --aplicar para valer.")
        return 0

    from subir_audio import cliente, subir
    s3, balde = cliente()
    TMP.mkdir(exist_ok=True)

    for e in pendentes:
        alvo = TMP / e["arquivo"]
        # ja esta la, com o tamanho certo? entao so reescreve a URL
        try:
            if s3.head_object(Bucket=balde, Key=e["arquivo"])["ContentLength"] == e["tamanho"]:
                print(f"  episodio {e['numero']}: ja estava no R2")
                e["url"] = f"{AUDIO}/{e['arquivo']}"
                continue
        except Exception:
            pass

        print(f"  episodio {e['numero']}: baixando do release...")
        urllib.request.urlretrieve(e["url"], alvo)
        if alvo.stat().st_size != e["tamanho"]:
            print(f"    ::error::baixou {alvo.stat().st_size:,} de {e['tamanho']:,}, pulando")
            continue
        subir(alvo, e["arquivo"])
        e["url"] = f"{AUDIO}/{e['arquivo']}"
        alvo.unlink()

    ESTADO.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run([sys.executable, str(RAIZ / "scripts" / "publicar_feed.py")], check=True)
    restantes = [e for e in d["episodios"] if not e["url"].startswith(AUDIO)]
    print(f"\nfeed reconstruido. {len(d['episodios']) - len(restantes)} de "
          f"{len(d['episodios'])} episodios no R2.")
    if restantes:
        print("AINDA NO GITHUB: " + ", ".join(str(e["numero"]) for e in restantes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
