# -*- coding: utf-8 -*-
"""Gera o audio de um episodio do COMPASSO CAPITAL a partir do roteiro do dia.

Roda no GitHub Actions, sem depender de nenhuma maquina ligada.

  python scripts/gerar_episodio.py <AAAA-MM-DD> <numero>

Procura roteiros/<AAAA-MM-DD>.md. Se nao existir, sai com codigo 0 e nao faz nada:
dia sem roteiro aprovado e dia sem episodio, e isso NAO e erro.
"""
import json, os, pathlib, re, subprocess, sys, urllib.request, urllib.error

RAIZ = pathlib.Path(__file__).resolve().parent.parent
AUDIO = RAIZ / "audio"
TMP = RAIZ / "_tmp"; TMP.mkdir(exist_ok=True)
KEY = os.environ.get("ELEVENLABS_API_KEY", "")
LEXICO = {k: v for k, v in json.loads((RAIZ / "scripts" / "lexico_pronuncia.json")
          .read_text(encoding="utf-8")).items() if not k.startswith("_")}

VOZ = {"DAVI": "2CECaLAGTS5NRGxgbcxr", "HELENA": "tZ2oxQJXfOrGrN7iKnta"}
TEMPO, ALVO_NOTICIA, ALVO_ANUNCIO = 1.02, 10.5, 22.0
ENTRADA_VOZ, LIMITE_API = 6.5, 1900
STINGS = {1: AUDIO / "sting_legale.wav", 2: AUDIO / "sting_iure.wav", 3: AUDIO / "sting_galicia.wav"}


def lex(t):
    for k in sorted(LEXICO, key=len, reverse=True):
        t = t.replace(k, LEXICO[k])
    return t


def ff(args):
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + args, check=True)


def dur(a):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(a)], capture_output=True, text=True).stdout.strip())


def media_db(a):
    s = subprocess.run(["ffmpeg", "-v", "info", "-i", str(a), "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.search(r"mean_volume: (-?[\d.]+) dB", s).group(1))


def tts(turnos):
    r = urllib.request.Request("https://api.elevenlabs.io/v1/text-to-dialogue",
        data=json.dumps({"inputs": turnos, "model_id": "eleven_v3",
                         "settings": {"stability": 0.0, "use_speaker_boost": True}}).encode(),
        headers={"xi-api-key": KEY, "Content-Type": "application/json"}, method="POST")
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(r, timeout=600) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            corpo = e.read().decode("utf-8", "ignore")[:300]
            if tentativa == 2:
                sys.exit(f"ERRO na ElevenLabs (HTTP {e.code}): {corpo}")
            print(f"  tentativa {tentativa+1} falhou ({e.code}), repetindo...")


def main():
    data, numero = sys.argv[1], int(sys.argv[2])
    roteiro = RAIZ / "roteiros" / f"{data}.md"

    if not roteiro.exists():
        print(f"sem roteiro para {data}: nada a fazer (isto nao e erro)")
        return 0
    if not KEY:
        sys.exit("ERRO: ELEVENLABS_API_KEY ausente no ambiente")

    texto = roteiro.read_text(encoding="utf-8").split("## FONTES")[0].replace(chr(92), "")
    segmentos, atual = [], None
    for linha in texto.splitlines():
        m = re.match(r"^## \[(BLOCO|ANUNCIO) (\d+)\]", linha.strip())
        if m:
            if atual: segmentos.append(atual)
            atual = {"tipo": m.group(1), "n": int(m.group(2)), "turnos": []}
            continue
        if atual is None: continue
        f = re.match(r"^\*\*(DAVI|HELENA):\*\*\s*(.+)$", linha.strip())
        if f:
            atual["turnos"].append({"text": lex(f.group(2).strip()), "voice_id": VOZ[f.group(1)]})
    if atual: segmentos.append(atual)

    if not segmentos:
        sys.exit("ERRO: roteiro existe mas nao tem bloco nenhum reconhecido")

    total = sum(len(t["text"]) for s in segmentos for t in s["turnos"])
    print(f"{len(segmentos)} segmentos, {total} caracteres")

    # ---------- gerar a voz ----------
    for i, s in enumerate(segmentos):
        lotes, lote, tam = [], [], 0
        for t in s["turnos"]:
            if tam + len(t["text"]) > LIMITE_API and lote:
                lotes.append(lote); lote, tam = [], 0
            lote.append(t); tam += len(t["text"])
        if lote: lotes.append(lote)
        print(f"  {s['tipo']} {s['n']}: {len(lotes)} chamada(s)")
        pedacos = []
        for j, l in enumerate(lotes):
            (TMP / f"s{i}_{j}.mp3").write_bytes(tts(l))
            ff(["-i", str(TMP / f"s{i}_{j}.mp3"), "-af", f"atempo={TEMPO}",
                "-ar", "44100", "-ac", "1", str(TMP / f"s{i}_{j}.wav")])
            pedacos.append(TMP / f"s{i}_{j}.wav")
        if len(pedacos) == 1:
            pedacos[0].replace(TMP / f"voz{i}.wav")
        else:
            lista = TMP / f"cat{i}.txt"
            lista.write_text("".join(f"file '{p}'\n" for p in pedacos), encoding="utf-8")
            ff(["-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(TMP / f"voz{i}.wav")])

    # ---------- envelope de trilha ----------
    db_voz = media_db(TMP / "voz0.wav")
    ref = TMP / "_ref.wav"
    ff(["-stream_loop", "-1", "-i", str(AUDIO / "cama.mp3"), "-t", "8", "-ar", "44100", "-ac", "1", str(ref)])
    db_cama = media_db(ref)
    g_not = (db_voz - ALVO_NOTICIA) - db_cama
    g_anu = (db_voz - ALVO_ANUNCIO) - db_cama

    def cama(dest, seg, ganho):
        if ganho is None:
            ff(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(seg), str(dest)])
        else:
            ff(["-stream_loop", "-1", "-i", str(AUDIO / "cama.mp3"), "-t", str(seg),
                "-af", f"volume={ganho}dB", "-ar", "44100", "-ac", "1", str(dest)])

    vozes, camas, ordem = [], [], 0
    for i, s in enumerate(segmentos):
        if s["tipo"] == "ANUNCIO" and s["n"] in STINGS and STINGS[s["n"]].exists():
            st = TMP / f"st{ordem}.wav"
            ff(["-i", str(STINGS[s["n"]]), "-ar", "44100", "-ac", "1", str(st)])
            sil = TMP / f"stsil{ordem}.wav"; cama(sil, dur(st), None)
            vozes.append(st); camas.append(sil); ordem += 1
        v = TMP / f"voz{i}.wav"
        c = TMP / f"cama{i}.wav"
        cama(c, dur(v), g_anu if s["tipo"] == "ANUNCIO" else g_not)
        vozes.append(v); camas.append(c)
        if i < len(segmentos) - 1:
            p = TMP / f"p{i}.wav"; ff(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.5", str(p)])
            pc = TMP / f"pc{i}.wav"; cama(pc, 0.5, g_anu if s["tipo"] == "ANUNCIO" else g_not)
            vozes.append(p); camas.append(pc)

    def juntar(lista, dest):
        arq = dest.with_suffix(".txt")
        arq.write_text("".join(f"file '{p}'\n" for p in lista), encoding="utf-8")
        ff(["-f", "concat", "-safe", "0", "-i", str(arq), "-ar", "44100", "-ac", "1", str(dest)])

    juntar(vozes, TMP / "voz_total.wav")
    juntar(camas, TMP / "cama_total.wav")
    ff(["-i", str(TMP / "cama_total.wav"), "-i", str(TMP / "voz_total.wav"), "-filter_complex",
        "[0:a][1:a]sidechaincompress=threshold=0.15:ratio=2:attack=20:release=300[o]",
        "-map", "[o]", str(TMP / "duck.wav")])
    ff(["-i", str(TMP / "voz_total.wav"), "-i", str(TMP / "duck.wav"), "-filter_complex",
        "[0:a][1:a]amix=inputs=2:normalize=0:duration=first[o]", "-map", "[o]", str(TMP / "mix.wav")])
    ff(["-i", str(AUDIO / "vinheta.mp3"), "-ar", "44100", "-ac", "1", str(TMP / "vin.wav")])

    saida = RAIZ / f"compasso-capital-{numero:04d}.mp3"
    ff(["-i", str(TMP / "vin.wav"), "-i", str(TMP / "mix.wav"), "-filter_complex",
        f"[1:a]adelay={int(ENTRADA_VOZ*1000)}|{int(ENTRADA_VOZ*1000)}[vd];"
        f"[vd]asplit=2[vm][ch];"
        f"[0:a][ch]sidechaincompress=threshold=0.08:ratio=6:attack=10:release=500[vdk];"
        f"[vdk][vm]amix=inputs=2:normalize=0:duration=longest,loudnorm=I=-16:TP=-1.5:LRA=11[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "192k", str(saida)])

    d = dur(saida)
    print(f"\nPRONTO: {saida.name} | {int(d//60)}min {int(d%60)}s | {saida.stat().st_size//1024//1024} MB")

    # deixa o resumo para os passos seguintes do workflow
    with open(os.environ.get("GITHUB_OUTPUT", TMP / "saida.txt"), "a", encoding="utf-8") as fh:
        fh.write(f"arquivo={saida.name}\n")
        fh.write(f"gerou=sim\n")
        fh.write(f"duracao={int(d//3600):02d}:{int(d%3600//60):02d}:{int(d%60):02d}\n")
        fh.write(f"tamanho={saida.stat().st_size}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
