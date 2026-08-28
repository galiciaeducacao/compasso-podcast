# -*- coding: utf-8 -*-
"""GUARDIAO: decide se um rascunho pode ir ao ar sem leitura humana.

Contexto: o Paulo dispensou a aprovacao manual. Isso significa que ESTE ARQUIVO e a
unica coisa entre o modelo e o ar, num programa diario que fala em nome de tres marcas
pagantes. A regua e deliberadamente dura: na duvida, barra. Um dia sem episodio e um
problema conhecido; um episodio com numero inventado e um problema que ninguem ve
ate ser tarde.

  python scripts/guardiao.py <AAAA-MM-DD>

Sai 0 e promove rascunhos/<data>.md para roteiros/<data>.md se TUDO passar.
Sai 1 sem promover, e explica cada reprovacao, se qualquer trava pegar.
"""
import json, os, pathlib, re, subprocess, sys, unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
LEXICO = {k: v for k, v in json.loads((RAIZ / "scripts" / "lexico_pronuncia.json")
          .read_text(encoding="utf-8")).items() if not k.startswith("_")}
TETO_BLOCO = 1900   # margem de lote do gerador; o priming conta junto, ver regra 1
TETO_RISO = 0.15
QUARENTENA = 30          # episodios em que uma reacao nao pode se repetir
CUSTO_ESTIMADO = 15000

UNI = {"zero":0,"um":1,"uma":1,"dois":2,"duas":2,"tres":3,"quatro":4,"cinco":5,"seis":6,
       "sete":7,"oito":8,"nove":9,"dez":10,"onze":11,"doze":12,"treze":13,"catorze":14,
       "quatorze":14,"quinze":15,"dezesseis":16,"dezessete":17,"dezoito":18,"dezenove":19}
DEZ = {"vinte":20,"trinta":30,"quarenta":40,"cinquenta":50,"sessenta":60,"setenta":70,
       "oitenta":80,"noventa":90}
CEM = {"cem":100,"cento":100,"duzentos":200,"duzentas":200,"trezentos":300,"trezentas":300,
       "quatrocentos":400,"quatrocentas":400,"quinhentos":500,"quinhentas":500,
       "seiscentos":600,"seiscentas":600,"setecentos":700,"setecentas":700,
       "oitocentos":800,"oitocentas":800,"novecentos":900,"novecentas":900}
ESCALA = {"mil":1000,"milhao":10**6,"milhoes":10**6,"bilhao":10**9,"bilhoes":10**9,
          "trilhao":10**12,"trilhoes":10**12}


def norm_frase(s):
    """minusculas sem acento, PRESERVANDO os espacos (norm() cola tudo)"""
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def digitos_por_extenso(texto):
    """Cadeias de digitos que o roteiro fala por extenso.

    Nao calcula valor: concatena. "onze virgula dois" vira "112", que e exatamente
    o que o site escreve como "11,2%". Isso dispensa parser de decimal, que foi a
    parte que mais deu erro, e continua pegando o que interessa: numero dito no ar
    que nao existe na apuracao do dia.
    """
    limpo = re.sub(r"por\s+cento", " ", norm(texto))
    # a virgula nao pode simplesmente sumir: ela FECHA o grupo. Apagando-a,
    # "onze virgula dois" caia no mesmo grupo e virava 13 em vez de 11 e 2.
    limpo = re.sub(r"\bvirgula\b", " virg ", limpo)
    palavras = re.findall(r"[a-z\u00e0-\u00fa]+", limpo)
    saida, cadeia, grupo, viu = [], "", 0, False

    def fechar_grupo():
        """dentro do grupo se SOMA (sessenta e cinco = 65); entre grupos se CONCATENA
        (onze | dois = 112), que e como o site escreve o decimal"""
        nonlocal cadeia, grupo
        if grupo:
            cadeia += str(grupo)
            grupo = 0

    for p_ in palavras:
        if p_ in UNI: grupo += UNI[p_]; viu = True
        elif p_ in DEZ: grupo += DEZ[p_]; viu = True
        elif p_ in CEM: grupo += CEM[p_]; viu = True
        elif p_ in ESCALA:
            # a escala nao entra na cadeia: "noventa e seis bilhoes" casa com o
            # "96,2 bilhoes" do site pela cadeia "96"
            fechar_grupo(); viu = True
        elif p_ == "virg":
            fechar_grupo(); viu = True
        elif p_ == "e":
            continue
        else:
            fechar_grupo()
            if viu and cadeia:
                saida.append(cadeia)
            cadeia, viu = "", False
    fechar_grupo()
    if viu and cadeia:
        saida.append(cadeia)
    return saida


def digitos_do_texto(texto):
    """Cadeias de digitos que aparecem escritas no site, sem separador."""
    return [re.sub(r"[^0-9]", "", m) for m in re.findall(r"\d[\d.,]*", texto)]

def analises_do_dia(data):
    """corpo das cinco analises publicadas no site naquele dia"""
    base = f"galicia/compasso/ops/diarias/{data}"
    r = subprocess.run(["gh", "api", f"repos/galiciaeducacao/claude-galicia/contents/{base}",
                        "--jq", '.[] | select(.name|endswith(".json")) | .name'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    # ordinais do site precisam virar cardinal: a analise escreve "sexagesimo quinto
    # mes" e o roteiro fala "sessenta e cinco meses". Sem isso, acusa alucinacao no
    # que e a mesma informacao dita de outro jeito.
    inteiro = []
    for nome in r.stdout.split():
        rr = subprocess.run(["gh", "api", f"repos/galiciaeducacao/claude-galicia/contents/{base}/{nome}",
                             "--jq", ".content"], capture_output=True, text=True)
        if rr.returncode == 0:
            import base64
            inteiro.append(base64.b64decode(rr.stdout.strip()).decode("utf-8", "ignore"))
    if not inteiro:
        return None
    junto = norm("\n".join(inteiro))
    # "sexagesimo quinto mes" no site tem de casar com "sessenta e cinco meses" no
    # roteiro: sem converter, o guardiao acusa alucinacao no que e o mesmo fato
    ORD = {"decimo": 10, "vigesimo": 20, "trigesimo": 30, "quadragesimo": 40,
           "quinquagesimo": 50, "sexagesimo": 60, "septuagesimo": 70,
           "octogesimo": 80, "nonagesimo": 90, "primeiro": 1, "segundo": 2,
           "terceiro": 3, "quarto": 4, "quinto": 5, "sexto": 6, "setimo": 7,
           "oitavo": 8, "nono": 9}
    chaves = "|".join(ORD)
    return re.sub(f"({chaves})" + r"\s+" + f"({chaves})",
                  lambda m: f" {ORD[m.group(1)] + ORD[m.group(2)]} ", junto)


def main():
    data = sys.argv[1]
    rascunho = RAIZ / "roteiros" / "rascunhos" / f"{data}.md"
    aprovado = RAIZ / "roteiros" / f"{data}.md"
    problemas = []

    if not rascunho.exists():
        print(f"sem rascunho para {data}: nada a promover")
        return 0
    if aprovado.exists():
        print(f"{data} ja esta aprovado")
        return 0

    texto = rascunho.read_text(encoding="utf-8").split("## FONTES")[0].replace(chr(92), "")

    # ---------- estrutura ----------
    blocos, atual = [], None
    for l in texto.splitlines():
        m = re.match(r"^## \[(BLOCO|ANUNCIO) (\d+)\]", l.strip())
        if m:
            if atual: blocos.append(atual)
            atual = {"tipo": m.group(1), "n": int(m.group(2)), "falas": []}
            continue
        if atual is None: continue
        f = re.match(r"^\*\*(DAVI|HELENA):\*\*\s*(.+)$", l.strip())
        if f: atual["falas"].append((f.group(1), f.group(2).strip()))
    if atual: blocos.append(atual)

    if not blocos:
        problemas.append("roteiro sem nenhum bloco reconhecido")
        blocos = []

    todas = [t for b in blocos for _, t in b["falas"]]

    # ---------- 1. o bloco cabe numa chamada so? ----------
    # Nao e um teto fixo. 2000 e o limite duro da API por chamada e 1900 e a margem
    # que o gerador usa para lotear, mas o numero que decide e outro: o gerador PREPENDE
    # a ultima fala do bloco anterior (o priming) antes de lotear, e o priming conta.
    # Bloco que estoura e partido em duas chamadas, e a emenda INTERNA nasce sem priming,
    # que e exatamente o defeito que o priming existe para evitar.
    #
    # Isso morde mais depois dos anuncios: o texto do oferecimento e uma fala unica e
    # longa, entao vira um priming caro para o bloco seguinte.
    # medido no texto JA TRADUZIDO pelo lexico, que e o que de fato vai para a API:
    # "IBGE" vira "Ibege e" e cresce, entao medir o texto cru subestima o bloco
    def lex(t):
        for k in sorted(LEXICO, key=len, reverse=True):
            t = t.replace(k, LEXICO[k])
        return t

    for i, b in enumerate(blocos):
        corpo = sum(len(lex(t)) for _, t in b["falas"])
        priming = len(lex(blocos[i - 1]["falas"][-1][1])) if i > 0 and blocos[i - 1]["falas"] else 0
        if corpo + priming > TETO_BLOCO:
            sobra = corpo + priming - TETO_BLOCO
            problemas.append(
                f"{b['tipo']} {b['n']} nao cabe numa chamada: {corpo} de fala mais "
                f"{priming} de priming = {corpo + priming} (teto {TETO_BLOCO}). "
                f"Cortar {sobra} caracteres, senao a emenda interna sai sem priming")

    # ---------- 2. maiuscula curta e numero em algarismo ----------
    for i, t in enumerate(todas, 1):
        sem_tag = re.sub(r"\[[^\]]+\]", "", t)
        for p in re.findall(r"\b[A-ZÀ-Ú]{2,6}\b", sem_tag):
            if p in ("COMPASSO", "CAPITAL", "DAVI", "HELENA"): continue
            if any(re.search(rf"\b{re.escape(p)}\b", k) for k in LEXICO): continue
            problemas.append(f"fala {i}: maiuscula curta '{p}' sera lida como sigla")
        for n in re.findall(r"\b\d+[\d.,]*\b", sem_tag):
            problemas.append(f"fala {i}: numero em algarismo '{n}', escrever por extenso")

    # ---------- 3. riso ----------
    riso = re.compile(r"\[(laughs?|chuckles?|giggles?)[^\]]*\]", re.I)
    marcados = [i for i, t in enumerate(todas) if riso.search(t)]
    if todas and len(marcados) / len(todas) > TETO_RISO:
        problemas.append(f"riso em {len(marcados)} de {len(todas)} turnos (teto {int(TETO_RISO*100)}%)")
    for a, b in zip(marcados, marcados[1:]):
        if b - a == 1:
            problemas.append(f"riso em turnos seguidos ({a+1} e {b+1})")

    # ---------- 4. eco: fala que devolve o que a outra acabou de dizer ----------
    def palavras(x):
        return set(re.findall(r"[a-zà-ú]{4,}", norm(re.sub(r"\[[^\]]+\]", "", x))))

    def sequencia(x):
        return re.findall(r"[a-zà-ú]+", norm(re.sub(r"\[[^\]]+\]", "", x)))

    def maior_trecho_repetido(a, b):
        """maior sequencia CONTIGUA de palavras que b repete de a, palavra por palavra"""
        melhor, linha = 0, [0] * (len(b) + 1)
        for pa in a:
            nova = [0] * (len(b) + 1)
            for j, pb in enumerate(b):
                if pa == pb:
                    nova[j + 1] = linha[j] + 1
                    melhor = max(melhor, nova[j + 1])
            linha = nova
        return melhor

    for i in range(1, len(todas)):
        a, b = palavras(todas[i-1]), palavras(todas[i])
        # confirmacao enfatica curta ('Nenhum.', 'O nosso Pix.') e recurso, nao eco
        if len(b) >= 5 and b and b <= a:
            problemas.append(f"fala {i+1} e eco da anterior: '{todas[i][:52]}'")
            continue
        # Eco PARCIAL, que o teste de subconjunto acima nao pega: a fala repete um
        # trecho inteiro da anterior e emenda algo novo no fim. Foi assim que passou
        # um "Parte da pressao nem e dirigida a gente" dito pelos dois seguidos.
        # So entre falas VIZINHAS: bordao repetido de longe e recurso da casa.
        n = maior_trecho_repetido(sequencia(todas[i-1]), sequencia(todas[i]))
        if n >= 5:
            problemas.append(
                f"fala {i+1} repete {n} palavras seguidas da anterior: '{todas[i][:60]}'")

    # ---------- 5. as tres marcas, uma por anuncio ----------
    anuncios = [b for b in blocos if b["tipo"] == "ANUNCIO"]
    for n, termo in ((1, "legale"), (2, "iure"), (3, "gal")):
        bloco = next((b for b in anuncios if b["n"] == n), None)
        if bloco is None:
            problemas.append(f"falta o [ANUNCIO {n}]")
        elif termo not in norm(" ".join(t for _, t in bloco["falas"])):
            problemas.append(f"[ANUNCIO {n}] nao cita a marca esperada")


    # ---------- 7. PERSPECTIVA TEMPORAL ----------
    # A fonte e sempre a analise da vespera, entao o texto nasce dizendo "hoje" sobre
    # fato de ontem. Um matinal que erra isso perde credibilidade depressa, e o erro e
    # invisivel para quem escreveu, porque na hora de escrever era mesmo hoje.
    #   fato ocorrido na vespera -> "ontem"
    #   agenda do proprio dia    -> "hoje"
    #   o proprio programa       -> "hoje" ("a escalacao de hoje")
    PRETERITO = (r"divulgou|anunciou|publicou|fechou|subiu|caiu|disse|afirmou|pediu|"
                 r"aprovou|registrou|bateu|recuou|avancou|decidiu|votou|assinou|cortou|"
                 r"elevou|derrubou|reagiu|abriu|encerrou|soltou|marcou|dobrou")
    for i, t_ in enumerate(todas, 1):
        limpo = norm_frase(re.sub(r"\[[^\]]+\]", "", t_))
        # "hoje" antes do verbo: "hoje o IBGE divulgou"
        if re.search(r"\bhoje\b(?:\s+\S+){0,5}\s+(?:" + PRETERITO + r")\b", limpo):
            problemas.append(f"fala {i}: diz 'hoje' sobre fato ja ocorrido, deveria ser 'ontem'")
        # "hoje" depois do verbo: "o IBGE divulgou hoje"
        elif re.search(r"\b(?:" + PRETERITO + r")\b(?:\s+\S+){0,3}\s+hoje\b", limpo):
            problemas.append(f"fala {i}: diz 'hoje' sobre fato ja ocorrido, deveria ser 'ontem'")

    # ---------- 6. LASTRO FACTUAL: nada que nao esteja nas analises da VESPERA ----------
    # O episodio de D comenta as analises publicadas em D-1, porque elas saem as 14h e
    # o programa vai ao ar as 7h da manha seguinte. Buscar a pasta de D acha pasta vazia
    # todo dia, e a regua reprovaria sempre.
    vespera = (dt.date.fromisoformat(data) - dt.timedelta(days=1)).isoformat()
    corpo = analises_do_dia(vespera)
    if corpo is None:
        problemas.append(f"nao consegui ler as analises de {vespera} para conferir os numeros")
    else:
        do_site = set(digitos_do_texto(corpo)) | set(digitos_por_extenso(corpo))
        # A conferencia vale para NOTICIA. O texto dos anuncios e institucional e fixo,
        # e a abertura fala do proprio programa (365 dias, sete da manha): nada disso
        # sai das analises, e cobrar lastro ali so gera ruido que ensina a ignorar o aviso.
        checaveis = []
        for b in blocos:
            if b["tipo"] == "ANUNCIO" or b["n"] == 0:
                continue
            checaveis += [x for _, x in b["falas"]]
        for i, t in enumerate(checaveis, 1):
            for n in digitos_por_extenso(re.sub(r"\[[^\]]+\]", "", t)):
                if len(n) < 2 or n in do_site:
                    continue
                # O site pode trazer o mesmo numero com mais casas decimais: o roteiro
                # fala "onze" e o site escreve "11,2". Mas prefixo SOLTO e frouxo demais
                # para a unica regra que separa numero inventado do ar: com 92 numeros na
                # apuracao, quase todo par de digitos e prefixo de alguma coisa. Entao o
                # prefixo so vale com diferenca de ate 2 digitos, que cobre decimal sem
                # deixar "12" casar com "1234567".
                if any((v.startswith(n) and len(v) - len(n) <= 2)
                       or (n.startswith(v) and len(n) - len(v) <= 2)
                       for v in do_site if len(v) >= 2):
                    continue
                problemas.append(f"fala {i}: numero '{n}' NAO aparece nas analises do dia")

    # ---------- 7. saldo ----------
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if key:
        import urllib.request
        try:
            r = urllib.request.Request("https://api.elevenlabs.io/v1/user/subscription",
                                       headers={"xi-api-key": key})
            with urllib.request.urlopen(r, timeout=60) as resp:
                s = json.loads(resp.read())
            resta = s["character_limit"] - s["character_count"]
            if resta < CUSTO_ESTIMADO:
                problemas.append(f"saldo de {resta:,} creditos, abaixo do custo de um episodio")
        except Exception:
            pass

    # ---------- veredito ----------
    if problemas:
        print(f"REPROVADO: {len(problemas)} problema(s)\n")
        for p in problemas:
            print(f"  - {p}")
        saida = os.environ.get("GITHUB_OUTPUT")
        if saida:
            with open(saida, "a", encoding="utf-8") as fh:
                fh.write("aprovado=nao\n")
                fh.write("motivos<<FIM\n" + "\n".join(f"- {p}" for p in problemas) + "\nFIM\n")
        return 1

    subprocess.run(["git", "mv", str(rascunho.relative_to(RAIZ)),
                    str(aprovado.relative_to(RAIZ))], cwd=RAIZ, check=True)
    print(f"APROVADO: {data} promovido para roteiros/, {len(blocos)} blocos, {len(todas)} falas")
    saida = os.environ.get("GITHUB_OUTPUT")
    if saida:
        with open(saida, "a", encoding="utf-8") as fh:
            fh.write("aprovado=sim\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
