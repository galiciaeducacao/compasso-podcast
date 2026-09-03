# -*- coding: utf-8 -*-
"""Gera o audio de um episodio do COMPASSO CAPITAL a partir do roteiro do dia.

Roda no GitHub Actions, sem depender de nenhuma maquina ligada.

  python scripts/gerar_episodio.py <AAAA-MM-DD> <numero>

Procura roteiros/<AAAA-MM-DD>.md. Se nao existir, sai com codigo 0 e nao faz nada:
dia sem roteiro aprovado e dia sem episodio, e isso NAO e erro.

CONTINUIDADE ENTRE BLOCOS (a armadilha mais cara do projeto)
Cada bloco e uma chamada separada e o modelo nao tem memoria entre chamadas: dentro
de uma chamada ele sabe como a fala anterior terminou, na seguinte comeca do zero, e
a voz muda de humor na emenda. Tres camadas resolvem:
  1. PRIMING: o bloco recebe colada no inicio a ultima fala do bloco anterior, e depois
     esse trecho e CORTADO do audio pela marcacao de tempo por palavra do Speech to Text.
  2. CONTINUIDADE EMOCIONAL: a primeira fala herda tag compativel com a ultima anterior.
  3. TAG EM TODA FALA: fala sem direcao e onde o modelo mais varia sozinho.

MIXAGEM DO OFERECIMENTO
No anuncio quem toca por baixo e a MUSICA DA PROPRIA MARCA, nao a cama do programa:
o sonic logo entra alto marcando a virada, e a mesma musica segue baixinho sob a
locucao, para nao ficar sem nada.
"""
import json, os, pathlib, re, subprocess, sys, unicodedata, uuid, urllib.request, urllib.error

RAIZ = pathlib.Path(__file__).resolve().parent.parent
AUDIO = RAIZ / "audio"
TMP = RAIZ / "_tmp"; TMP.mkdir(exist_ok=True)
KEY = os.environ.get("ELEVENLABS_API_KEY", "")
LEXICO = {k: v for k, v in json.loads((RAIZ / "scripts" / "lexico_pronuncia.json")
          .read_text(encoding="utf-8")).items() if not k.startswith("_")}

VOZ = {"DAVI": "2CECaLAGTS5NRGxgbcxr", "HELENA": "tZ2oxQJXfOrGrN7iKnta"}
TEMPO, ALVO_NOTICIA, ALVO_ANUNCIO = 1.02, 10.5, 20.0
ENTRADA_VOZ, LIMITE_API = 6.5, 1900
CUSTO_ESTIMADO = 15000   # um episodio completo, ja com o priming
MARCAS = {1: ("legale", "Legale"), 2: ("iure", "Iure Digital"), 3: ("galicia", "Galícia")}
COMPATIVEL = {"very excited": "excited", "very very excited": "excited",
              "very very very excited": "excited", "excited": "excited",
              "very serious": "serious", "serious": "serious",
              "thoughtful": "thoughtful", "amused": "amused", "warmly": "warmly"}


def lex(t):
    for k in sorted(LEXICO, key=len, reverse=True):
        t = t.replace(k, LEXICO[k])
    return t


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


def ff(args):
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + args, check=True)


def dur(a):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(a)], capture_output=True, text=True).stdout.strip())


def media_db(a):
    s = subprocess.run(["ffmpeg", "-v", "info", "-i", str(a), "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.search(r"mean_volume: (-?[\d.]+) dB", s).group(1))


def tts(turnos, destino):
    r = urllib.request.Request("https://api.elevenlabs.io/v1/text-to-dialogue",
        data=json.dumps({"inputs": turnos, "model_id": "eleven_v3",
                         "settings": {"stability": 0.0, "use_speaker_boost": True}}).encode(),
        headers={"xi-api-key": KEY, "Content-Type": "application/json"}, method="POST")
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(r, timeout=600) as resp:
                destino.write_bytes(resp.read())
                return
        except urllib.error.HTTPError as e:
            if tentativa == 2:
                sys.exit(f"ERRO na ElevenLabs (HTTP {e.code}): {e.read().decode('utf-8','ignore')[:300]}")


def palavras_com_tempo(arq):
    lim = "----" + uuid.uuid4().hex
    corpo = b""
    for c, v in (("model_id", "scribe_v1"), ("language_code", "por"),
                 ("timestamps_granularity", "word")):
        corpo += f"--{lim}\r\nContent-Disposition: form-data; name=\"{c}\"\r\n\r\n{v}\r\n".encode()
    corpo += (f"--{lim}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.wav\"\r\n"
              f"Content-Type: audio/wav\r\n\r\n").encode() + arq.read_bytes() + f"\r\n--{lim}--\r\n".encode()
    r = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", data=corpo,
        headers={"xi-api-key": KEY, "Content-Type": f"multipart/form-data; boundary={lim}"}, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=900) as resp:
            return [w for w in json.loads(resp.read()).get("words", []) if norm(w.get("text", ""))]
    except Exception:
        return []


def inicio_do_bloco(arq, texto_contexto, texto_primeira):
    """Segundo em que COMECA a primeira fala do bloco, que e onde o priming acaba.

    Ancora no inicio da fala nova, nunca no fim do contexto: o contexto costuma
    terminar em endereco de site, e a transcricao devolve isso como uma palavra so,
    que nunca casa. Quando a ancora completa falha, cai para a primeira palavra
    distintiva, isto e, uma palavra da fala nova que nao aparece no contexto.

    Devolve None quando nao tem certeza. Quem chama aborta, porque um corte errado
    vai ao ar comendo o comeco da frase ou repetindo a anterior, e ninguem escuta
    365 episodios por ano para pegar isso.
    """
    palavras = palavras_com_tempo(arq)
    if not palavras:
        return None
    lidas = [norm(w["text"]) for w in palavras]
    ctx = [norm(x) for x in texto_contexto.split() if norm(x)]
    nova = [norm(x) for x in re.sub(r"\[[^\]]*\]\s*", "", texto_primeira).split() if norm(x)]
    if not nova:
        return None

    # O tempo de inicio da palavra cai no ataque da consoante, um pouco depois do
    # comeco real do som. Cortar exatamente ali come o primeiro fonema, entao recua
    # um respiro. O que entra nesse respiro e silencio entre falas.
    MARGEM = 0.12

    def em(k):
        return max(0.0, float(palavras[k]["start"]) - MARGEM)

    # a fala nova nao comeca antes de metade do contexto ter sido dita
    piso = max(0, int(len(ctx) * 0.5))

    # 1) ancora completa: as primeiras palavras da fala nova, em sequencia
    n = min(4, len(nova))
    for k in range(piso, len(lidas) - n + 1):
        if lidas[k:k + n] == nova[:n]:
            return em(k)

    # 2) queda: primeira palavra distintiva, isto e, da fala nova e ausente do contexto.
    # Exige 4 letras ou mais: "que", "nao", "com" casam em qualquer ponto da transcricao
    # e levariam o corte para o meio do contexto.
    no_contexto = set(ctx)
    for idx, palavra in enumerate(nova):
        if palavra in no_contexto or len(palavra) < 4:
            continue
        # comeca a busca em idx: achar a palavra antes disso tornaria o recuo impossivel,
        # e k - idx negativo daria a volta na lista sem erro nenhum, cortando em ponto
        # aleatorio do audio
        for k in range(max(piso, idx), len(lidas)):
            if lidas[k] == palavra:
                # recua o tanto da fala nova que ja foi dito antes dessa palavra
                return em(k - idx)

    # 3) ultima queda: a primeira palavra da fala nova, e SO se ela aparecer uma unica
    # vez na regiao. Sem essa exigencia, uma abertura comum ("mas", "entao") casaria em
    # varios pontos e o corte viraria sorteio, que e pior que abortar.
    ocorrencias = [k for k in range(piso, len(lidas)) if lidas[k] == nova[0]]
    if len(ocorrencias) == 1:
        return em(ocorrencias[0])
    return None


def main():
    data, numero = sys.argv[1], int(sys.argv[2])
    roteiro = RAIZ / "roteiros" / f"{data}.md"
    if not roteiro.exists():
        print(f"sem roteiro para {data}: nada a fazer (isto nao e erro)")
        return 0
    if not KEY:
        sys.exit("ERRO: ELEVENLABS_API_KEY ausente no ambiente")

    # saldo: melhor falhar avisando do que na metade do episodio
    try:
        r = urllib.request.Request("https://api.elevenlabs.io/v1/user/subscription",
                                   headers={"xi-api-key": KEY})
        with urllib.request.urlopen(r, timeout=60) as resp:
            s = json.loads(resp.read())
        resta = s["character_limit"] - s["character_count"]
        print(f"creditos restantes: {resta:,}")
        if resta < CUSTO_ESTIMADO:
            print(f"::error::Saldo insuficiente: restam {resta:,} e um episodio custa cerca "
                  f"de {CUSTO_ESTIMADO:,}. Nada foi gerado.")
            sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"::warning::Nao consegui checar o saldo (HTTP {e.code}). Seguindo mesmo assim.")

    # ---------- parse ----------
    texto = roteiro.read_text(encoding="utf-8").split("## FONTES")[0].replace(chr(92), "")
    segs, atual = [], None
    for l in texto.splitlines():
        m = re.match(r"^## \[(BLOCO|ANUNCIO) (\d+)\]", l.strip())
        if m:
            if atual: segs.append(atual)
            atual = {"tipo": m.group(1), "n": int(m.group(2)), "turnos": [],
                     "titulo": l.strip()[m.end():].strip()}
            continue
        if atual is None: continue
        f = re.match(r"^\*\*(DAVI|HELENA):\*\*\s*(.+)$", l.strip())
        if f:
            bruto = f.group(2).strip()
            tag = re.match(r"^\[([^\]]+)\]", bruto)
            atual["turnos"].append({"quem": f.group(1),
                                    "tag": tag.group(1) if tag else None,
                                    "texto": lex(bruto)})
    if atual: segs.append(atual)
    if not segs:
        sys.exit("ERRO: roteiro sem bloco reconhecido")

    # ---------- camada 3: nenhuma fala sem direcao ----------
    sem_tag = 0
    for s in segs:
        for t in s["turnos"]:
            if t["tag"] is None:
                t["tag"] = "warmly"
                t["texto"] = "[warmly] " + t["texto"]
                sem_tag += 1

    # ---------- camada 2: humor alinhado nas emendas ----------
    ajustes = 0
    for i in range(1, len(segs)):
        ultima = segs[i-1]["turnos"][-1]["tag"]
        primeira = segs[i]["turnos"][0]
        clima = COMPATIVEL.get(ultima, ultima)
        if COMPATIVEL.get(primeira["tag"], primeira["tag"]) != clima:
            primeira["texto"] = re.sub(r"^\[[^\]]+\]", f"[{clima}]", primeira["texto"])
            primeira["tag"] = clima
            ajustes += 1

    print(f"{len(segs)} segmentos | {sem_tag} falas ganharam direcao | {ajustes} emendas alinhadas")

    # ---------- camada 1: priming + corte ----------
    # Anuncio com audio pre-gravado nao passa pela API: o texto e fixo, entao gerar
    # todo dia so cria tres chances diarias de a pronuncia sair diferente, e queima
    # cerca de 900 creditos por dia a toa. Se audio/anuncio_<marca>.mp3 existir, ele
    # e usado como esta.
    total = 0
    sem_corte = []
    for i, s in enumerate(segs):
        marca_i = MARCAS.get(s["n"], (None, None))[0] if s["tipo"] == "ANUNCIO" else None
        if marca_i and (AUDIO / f"anuncio_{marca_i}.mp3").exists():
            ff(["-i", str(AUDIO / f"anuncio_{marca_i}.mp3"), "-ar", "44100", "-ac", "1",
                str(TMP / f"v{i}.wav")])
            print(f"  {s['tipo']} {s['n']}: audio fixo da marca (0 creditos)")
            continue
        entradas = [{"text": t["texto"], "voice_id": VOZ[t["quem"]]} for t in s["turnos"]]
        contexto = None
        if i > 0:
            ant = segs[i-1]["turnos"][-1]
            contexto = re.sub(r"\[[^\]]*\]\s*", "", ant["texto"]).strip()
            entradas.insert(0, {"text": ant["texto"], "voice_id": VOZ[ant["quem"]]})

        # respeita o teto da API quebrando em lotes
        lotes, lote, tam = [], [], 0
        for e in entradas:
            if tam + len(e["text"]) > LIMITE_API and lote:
                lotes.append(lote); lote, tam = [], 0
            lote.append(e); tam += len(e["text"])
        if lote: lotes.append(lote)
        total += sum(len(e["text"]) for e in entradas)

        pedacos = []
        for j, l in enumerate(lotes):
            tts(l, TMP / f"b{i}_{j}.mp3")
            ff(["-i", str(TMP / f"b{i}_{j}.mp3"), "-ar", "44100", "-ac", "1", str(TMP / f"r{i}_{j}.wav")])
            pedacos.append(TMP / f"r{i}_{j}.wav")
        if len(pedacos) == 1:
            bruto = pedacos[0]
        else:
            lista = TMP / f"cat{i}.txt"
            lista.write_text("".join(f"file '{p}'\n" for p in pedacos), encoding="utf-8")
            bruto = TMP / f"raw{i}.wav"
            ff(["-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(bruto)])

        destino = TMP / f"voz{i}.wav"
        if contexto:
            corte = inicio_do_bloco(bruto, contexto, s["turnos"][0]["texto"])
            if corte:
                ff(["-ss", f"{corte:.3f}", "-i", str(bruto), "-ar", "44100", "-ac", "1", str(destino)])
                print(f"  bloco {i}: priming cortado em {corte:.2f}s")
            else:
                bruto.replace(destino)
                sem_corte.append(i)
                print(f"  bloco {i}: NAO achei o corte do priming")
        else:
            bruto.replace(destino)
        ff(["-i", str(destino), "-af", f"atempo={TEMPO}", "-ar", "44100", "-ac", "1", str(TMP / f"v{i}.wav")])

    # Fala repetida no ar e pior que episodio nao publicado: quem ouve percebe na
    # hora e ninguem revisa 365 episodios por ano. Entao para aqui, com a lista.
    if sem_corte:
        print(f"::error::Nao localizei o corte do priming nos blocos {sem_corte}. "
              f"Cada um deles ficaria com a fala anterior repetida no ar. Nada foi montado.")
        sys.exit(1)

    # ---------- envelope: cada trecho com sua trilha ----------
    db_voz = media_db(TMP / "v0.wav")
    ref = TMP / "_ref.wav"
    ff(["-stream_loop", "-1", "-i", str(AUDIO / "cama.mp3"), "-t", "8", "-ar", "44100", "-ac", "1", str(ref)])
    g_not = (db_voz - ALVO_NOTICIA) - media_db(ref)

    def trilha(dest, seg, fonte, ganho):
        if fonte is None:
            ff(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(seg), str(dest)])
        else:
            ff(["-stream_loop", "-1", "-i", str(fonte), "-t", str(seg),
                "-af", f"volume={ganho}dB", "-ar", "44100", "-ac", "1", str(dest)])

    vozes, camas, ordem = [], [], 0
    for i, s in enumerate(segs):
        v = TMP / f"v{i}.wav"
        marca = MARCAS.get(s["n"], (None, None))[0] if s["tipo"] == "ANUNCIO" else None

        if marca and (AUDIO / f"sting_{marca}.wav").exists():
            st = TMP / f"st{ordem}.wav"
            ff(["-i", str(AUDIO / f"sting_{marca}.wav"), "-ar", "44100", "-ac", "1", str(st)])
            sil = TMP / f"sts{ordem}.wav"; trilha(sil, dur(st), None, 0)
            vozes.append(st); camas.append(sil); ordem += 1

        # VAR: o apito do arbitro marca a virada para o bloco de explicacao. Pedido do
        # Paulo em 03/09: chamar o VAR de verdade, com som, para o publico aprender o
        # que cada parte do programa faz. Vale para todo BLOCO cujo titulo comeca com VAR.
        if s["tipo"] == "BLOCO" and s.get("titulo", "").upper().startswith("VAR") \
                and (AUDIO / "sting_var.wav").exists():
            st = TMP / f"st{ordem}.wav"
            ff(["-i", str(AUDIO / "sting_var.wav"), "-ar", "44100", "-ac", "1", str(st)])
            sil = TMP / f"sts{ordem}.wav"; trilha(sil, dur(st), None, 0)
            vozes.append(st); camas.append(sil); ordem += 1
            print(f"  bloco {i}: apito do VAR")

        c = TMP / f"c{i}.wav"
        if marca and (AUDIO / f"musica_{marca}.mp3").exists():
            # sob o oferecimento toca a musica DA MARCA, nao a cama do programa
            m = AUDIO / f"musica_{marca}.mp3"
            ref_m = TMP / f"refm{i}.wav"
            ff(["-stream_loop", "-1", "-i", str(m), "-t", "6", "-ar", "44100", "-ac", "1", str(ref_m)])
            trilha(c, dur(v), m, (db_voz - ALVO_ANUNCIO) - media_db(ref_m))
        else:
            trilha(c, dur(v), AUDIO / "cama.mp3", g_not)
        vozes.append(v); camas.append(c)

        # assinatura de SAIDA: fecha o oferecimento e devolve a noticia sem secura
        if marca and (AUDIO / f"saida_{marca}.wav").exists():
            sa = TMP / f"sa{ordem}.wav"
            ff(["-i", str(AUDIO / f"saida_{marca}.wav"), "-ar", "44100", "-ac", "1", str(sa)])
            sil = TMP / f"sas{ordem}.wav"; trilha(sil, dur(sa), None, 0)
            vozes.append(sa); camas.append(sil); ordem += 1

        if i < len(segs) - 1:
            p = TMP / f"p{i}.wav"; ff(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.5", str(p)])
            pc = TMP / f"pc{i}.wav"; trilha(pc, 0.5, AUDIO / "cama.mp3", g_not)
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
    print(f"\nPRONTO: {saida.name} | {int(d//60)}min {int(d%60)}s | ~{total} creditos")
    with open(os.environ.get("GITHUB_OUTPUT", TMP / "saida.txt"), "a", encoding="utf-8") as fh:
        fh.write(f"arquivo={saida.name}\ngerou=sim\n")
        fh.write(f"duracao={int(d//3600):02d}:{int(d%3600//60):02d}:{int(d%60):02d}\n")
        fh.write(f"tamanho={saida.stat().st_size}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
