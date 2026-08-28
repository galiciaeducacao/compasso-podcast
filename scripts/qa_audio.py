# -*- coding: utf-8 -*-
"""QA do audio gerado, antes de ele virar release.

  python scripts/qa_audio.py <arquivo.mp3> <AAAA-MM-DD>

Existe porque o gerador pode terminar com exito e ainda assim entregar um episodio
quebrado: um bloco que a API devolveu truncado, um corte de priming no lugar errado
que deixa fala repetida, uma mixagem que ficou muda. Nada disso levanta excecao, e
num programa diario ninguem escuta 12 minutos antes de publicar.

O teste central e comparar a TRANSCRICAO do audio com o ROTEIRO. E o unico jeito de
saber que o que foi escrito e o que foi dito.

Sai 1 e imprime ::error:: se reprovar. Quem chama nao deve publicar.
"""
import json, os, pathlib, re, subprocess, sys, unicodedata, uuid, urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
KEY = os.environ.get("ELEVENLABS_API_KEY", "")

VOLUME_ALVO = -16.0      # loudnorm mira -16 LUFS
VOLUME_FOLGA = 2.0
PICO_MAX = -0.5          # acima disso e risco de clipping no tocador
COBERTURA_MIN = 0.92     # fracao das falas que precisa aparecer na transcricao
REPETICAO_MAX = 12       # palavras seguidas repetidas no audio inteiro


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def falar(caminho):
    """transcricao do audio, como lista de palavras normalizadas"""
    lim = "----" + uuid.uuid4().hex
    corpo = b""
    for c, v in (("model_id", "scribe_v1"), ("language_code", "por")):
        corpo += f"--{lim}\r\nContent-Disposition: form-data; name=\"{c}\"\r\n\r\n{v}\r\n".encode()
    corpo += (f"--{lim}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.mp3\"\r\n"
              f"Content-Type: audio/mpeg\r\n\r\n").encode() + caminho.read_bytes() \
             + f"\r\n--{lim}--\r\n".encode()
    r = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", data=corpo,
        headers={"xi-api-key": KEY, "Content-Type": f"multipart/form-data; boundary={lim}"},
        method="POST")
    with urllib.request.urlopen(r, timeout=900) as resp:
        return norm(json.loads(resp.read()).get("text", "")).split()


def medida(caminho, filtro, padrao):
    s = subprocess.run(["ffmpeg", "-v", "info", "-i", str(caminho), "-af", filtro,
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(padrao, s)
    return float(m.group(1)) if m else None


def falas_do_roteiro(data):
    t = (RAIZ / "roteiros" / f"{data}.md").read_text(encoding="utf-8")
    t = t.split("## FONTES")[0].replace(chr(92), "")
    return [m[1] for m in re.findall(r"^\*\*(DAVI|HELENA):\*\*\s*(.+)$", t, re.M)]


def main():
    arq, data = pathlib.Path(sys.argv[1]), sys.argv[2]
    problemas, avisos = [], []

    # ---------- 1. o arquivo e audio valido e tem duracao plausivel ----------
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", str(arq)],
                               capture_output=True, text=True).stdout.strip() or 0)
    if dur < 60:
        problemas.append(f"audio com {dur:.0f}s: curto demais para um episodio")

    falas = falas_do_roteiro(data)
    escrito = sum(len(re.sub(r"\[[^\]]+\]", "", f).strip()) for f in falas)
    # 15,2 caracteres por segundo, SEM as tags de direcao, que ninguem fala: medido
    # no episodio 1, 11.434 caracteres em 753s, com erro de 1,5%. O chute inicial era
    # 14 com as tags dentro, e por causa dele eu li um roteiro de 13 minutos como 17.
    esperado = escrito / 15.2
    if not 0.6 * esperado < dur < 1.6 * esperado:
        problemas.append(f"duracao {dur:.0f}s fora do esperado (~{esperado:.0f}s "
                         f"para {escrito} caracteres de fala)")

    # ---------- 2. volume ----------
    media = medida(arq, "volumedetect", r"mean_volume: (-?[\d.]+) dB")
    pico = medida(arq, "volumedetect", r"max_volume: (-?[\d.]+) dB")
    if media is None:
        problemas.append("nao consegui medir o volume")
    elif abs(media - VOLUME_ALVO) > VOLUME_FOLGA:
        problemas.append(f"volume medio {media} dB, fora de {VOLUME_ALVO} +/- {VOLUME_FOLGA}")
    if pico is not None and pico > PICO_MAX:
        problemas.append(f"pico {pico} dB: risco de estourar no tocador")

    # ---------- 3. a trilha esta la? ----------
    # silencio de verdade so aparece se a cama sumiu: no programa ela toca inteira
    s = subprocess.run(["ffmpeg", "-v", "info", "-i", str(arq), "-af",
                        "silencedetect=n=-45dB:d=1.5", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    mudos = len(re.findall(r"silence_start", s))
    if mudos:
        problemas.append(f"{mudos} trecho(s) de silencio real: a trilha caiu")

    # ---------- 4. o que foi escrito foi dito? ----------
    if not KEY:
        avisos.append("sem ELEVENLABS_API_KEY: pulei a conferencia contra o roteiro")
    else:
        dito = falar(arq)
        texto_dito = " " + " ".join(dito) + " "

        # 4a. cobertura: cada fala deixou rastro, e na ordem
        achadas, perdidas, cursor = 0, [], 0
        for i, f in enumerate(falas, 1):
            p = norm(re.sub(r"\[[^\]]+\]", "", f)).split()
            if len(p) < 4:
                achadas += 1     # fala curta demais para ancorar; nao conta contra
                continue
            alvo = " ".join(p[:4])
            pos = " ".join(dito[cursor:]).find(alvo)
            if pos >= 0:
                achadas += 1
                cursor += len(" ".join(dito[cursor:])[:pos].split())
            elif alvo in texto_dito:
                achadas += 1     # apareceu, mas fora de ordem: a transcricao erra ordem as vezes
            else:
                perdidas.append((i, f[:60]))
        cobertura = achadas / len(falas) if falas else 0
        if cobertura < COBERTURA_MIN:
            problemas.append(f"so {cobertura:.0%} das falas apareceram no audio "
                             f"(minimo {COBERTURA_MIN:.0%}). Faltando: "
                             + "; ".join(f"fala {i} '{t}'" for i, t in perdidas[:5]))
        else:
            print(f"cobertura: {cobertura:.0%} das {len(falas)} falas")
            for i, t in perdidas:
                avisos.append(f"fala {i} nao localizada na transcricao: '{t}'")

        # 4b. repeticao no AUDIO: e assim que um priming mal cortado aparece
        vistos, repetidos = {}, []
        for j in range(len(dito) - REPETICAO_MAX + 1):
            seq = " ".join(dito[j:j + REPETICAO_MAX])
            if seq in vistos:
                repetidos.append((seq, vistos[seq], j))
            else:
                vistos[seq] = j
        if repetidos:
            seq, a, b = repetidos[0]
            problemas.append(f"{len(repetidos)} trecho(s) de {REPETICAO_MAX} palavras ditos "
                             f"duas vezes (priming mal cortado?): '{seq[:70]}' "
                             f"nas posicoes {a} e {b}")

    for a in avisos:
        print(f"::warning::{a}")
    if problemas:
        for p in problemas:
            print(f"::error::{p}")
        print(f"\nQA REPROVOU o audio ({len(problemas)} problema(s)). Nao publicar.")
        return 1
    print(f"\nQA APROVOU: {int(dur//60)}min {int(dur%60)}s | volume {media} dB | pico {pico} dB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
