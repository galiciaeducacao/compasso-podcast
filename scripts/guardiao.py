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
import datetime as dt
import json, os, pathlib, re, subprocess, sys, unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
LEXICO = {k: v for k, v in json.loads((RAIZ / "scripts" / "lexico_pronuncia.json")
          .read_text(encoding="utf-8")).items() if not k.startswith("_")}
TETO_BLOCO = 1900   # margem de lote do gerador; o priming conta junto, ver regra 1
HOST, ANALISTA = "HELENA", "DAVI"   # decisao do Paulo, 03/09/2026, ouvindo tres testes:
                                    # a Helena apresenta e chama os lances, o Davi analisa
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
    aberto = False   # o grupo comecou, mesmo que valha zero

    def fechar_grupo():
        """dentro do grupo se SOMA (sessenta e cinco = 65); entre grupos se CONCATENA
        (onze | dois = 112), que e como o site escreve o decimal.

        O grupo fecha pelo que foi DITO, nao pelo valor: "zero virgula quarenta e sete"
        tem um grupo zero antes da virgula, e o site escreve "0,47". Testar `if grupo`
        apagava esse zero e produzia "47", que nao casa com "047" nem por prefixo. O
        defeito passava despercebido porque todo decimal de uma casa ("zero virgula
        cinco") virava cadeia de um digito, curta demais para a regra 6 conferir.
        """
        nonlocal cadeia, grupo, aberto
        if aberto:
            cadeia += str(grupo)
            grupo, aberto = 0, False

    for k_, p_ in enumerate(palavras):
        # "mil" seguido de mais numero ("dois mil e vinte e dois", "mil novecentos e
        # oitenta e dois", "duas mil e duas") e MULTIPLICADOR: vira 2022, 1982, 2002.
        # O Paulo escreve ano por extenso e o texto manda; o parser se adapta.
        # "mil" seguido de palavra comum ("cento e vinte e oito mil toneladas") continua
        # fechando o grupo, porque o site escreve "128 mil" e a cadeia certa e "128".
        if p_ == "mil":
            prox = next((w for w in palavras[k_ + 1:] if w != "e"), None)
            if prox in UNI or prox in DEZ or prox in CEM:
                grupo = (grupo if aberto and grupo else 1) * 1000
                viu = aberto = True
                continue
        if p_ in UNI: grupo += UNI[p_]; viu = aberto = True
        elif p_ in DEZ: grupo += DEZ[p_]; viu = aberto = True
        elif p_ in CEM: grupo += CEM[p_]; viu = aberto = True
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

def analises_por_gh(base):
    """le as analises pela API do GitHub. None se o gh nao existe ou nao respondeu.

    O gh AUSENTE tem de cair no mesmo None que o gh que falha: sem isso o
    FileNotFoundError sobe e mata o guardiao ANTES do veredito, e a regua nao
    reprova nem aprova, so estoura. Mesmo defeito do import que faltava.
    """
    try:
        r = subprocess.run(["gh", "api", f"repos/galiciaeducacao/claude-galicia/contents/{base}",
                            "--jq", '.[] | select(.name|endswith(".json")) | .name'],
                           capture_output=True, text=True)
    except (FileNotFoundError, OSError):
        return None
    if r.returncode != 0:
        return None
    inteiro = []
    for nome in r.stdout.split():
        rr = subprocess.run(["gh", "api", f"repos/galiciaeducacao/claude-galicia/contents/{base}/{nome}",
                             "--jq", ".content"], capture_output=True, text=True)
        if rr.returncode == 0:
            import base64
            inteiro.append(base64.b64decode(rr.stdout.strip()).decode("utf-8", "ignore"))
    return inteiro or None


def analises_por_clone(base):
    """le as mesmas analises de um checkout local do claude-galicia, quando existir.

    Nao afrouxa nada: sao os mesmos arquivos, conferidos com o mesmo rigor. Existe
    para o ambiente que roda o guardiao sem o gh instalado, onde a alternativa nao
    e uma regua mais frouxa, e sim regua nenhuma.
    """
    for raiz in (os.environ.get("CLAUDE_GALICIA_DIR"), RAIZ.parent / "claude-galicia"):
        if not raiz:
            continue
        pasta = pathlib.Path(raiz) / base
        if not pasta.is_dir():
            continue
        inteiro = [p.read_text(encoding="utf-8", errors="ignore")
                   for p in sorted(pasta.glob("*.json"))]
        if inteiro:
            return inteiro
    return None


def analises_do_dia(data):
    """corpo das cinco analises publicadas no site naquele dia"""
    base = f"galicia/compasso/ops/diarias/{data}"
    inteiro = analises_por_gh(base) or analises_por_clone(base)
    if not inteiro:
        return None
    # ordinais do site precisam virar cardinal: a analise escreve "sexagesimo quinto
    # mes" e o roteiro fala "sessenta e cinco meses". Sem isso, acusa alucinacao no
    # que e a mesma informacao dita de outro jeito.
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
        # Sem rascunho E sem roteiro aprovado, o dia simplesmente nao vai existir. Isso
        # nao pode acontecer calado: e a falha mais provavel da esteira (a rotina que
        # escreve nao rodou, ou nao achou a apuracao) e a mais dificil de perceber,
        # porque nada quebra, nada estoura, so nao sai episodio.
        if not aprovado.exists():
            print(f"::error::Nao existe roteiro nem rascunho para {data}. "
                  f"Se nada for feito, NAO HAVERA EPISODIO nesse dia.")
            saida = os.environ.get("GITHUB_OUTPUT")
            if saida:
                with open(saida, "a", encoding="utf-8") as fh:
                    fh.write("faltando=sim\n")
            return 0
        print(f"sem rascunho para {data}: o roteiro ja esta aprovado")
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
            atual = {"tipo": m.group(1), "n": int(m.group(2)), "falas": [],
                     "titulo": l.strip()[m.end():].strip()}
            continue
        if atual is None: continue
        f = re.match(r"^\*\*(DAVI|HELENA):\*\*\s*(.+)$", l.strip())
        if f: atual["falas"].append((f.group(1), f.group(2).strip()))
    if atual: blocos.append(atual)

    if not blocos:
        problemas.append("roteiro sem nenhum bloco reconhecido")
        blocos = []

    todas = [t for b in blocos for _, t in b["falas"]]
    # quem diz cada fala, na mesma ordem de `todas`: a regra 4c precisa saber se a
    # voz mudou, porque jogral e devolver a palavra do OUTRO, nao retomar a propria
    quem = [q for b in blocos for q, _ in b["falas"]]

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

    # ---------- 4b. ECO CURTO: devolver a frase em vez de reagir ----------
    # O limiar de 5 palavras acima nasceu de um eco longo e deixa passar o curto, que
    # e o mais comum: "Antes do almoco?" / "Antes do almoco." Sao duas coisas distintas.
    #
    # REPETICAO IDENTICA nunca presta, de qualquer tamanho: devolver a mesma frase nao
    # e reagir. O episodio aprovado nao tem nenhuma.
    #
    # ECO QUE CONDENSA e recurso legitimo: "Nenhum dolar? Da China inteira?" seguido de
    # "Nenhum." O aprovado tem dois, em 168 falas. O problema e a DENSIDADE: o primeiro
    # roteiro automatico veio com onze em 219, e onze viram cacoete mesmo quando cada um
    # passaria sozinho. Por isso teto, nao proibicao.
    ecos = []
    for i in range(1, len(todas)):
        a, b = palavras(todas[i-1]), palavras(todas[i])
        if not b or not (b <= a):
            continue
        ecos.append(i + 1)
        so_a = " ".join(sequencia(todas[i-1]))
        so_b = " ".join(sequencia(todas[i]))
        if so_a == so_b:
            problemas.append(
                f"fala {i+1} repete a anterior palavra por palavra: '{todas[i][:60]}'. "
                f"Devolver a frase nao e reagir")
    if todas and len(ecos) / len(todas) > 0.03:
        problemas.append(
            f"{len(ecos)} falas de {len(todas)} ({len(ecos)/len(todas):.0%}) so devolvem "
            f"palavras da fala anterior, sem acrescentar (teto 3%, o episodio aprovado "
            f"tem 1%). Vira cacoete. Falas: {ecos[:8]}")

    # ---------- 4c. JOGRAL: pegar a palavra da fala anterior e devolver ----------
    # Regra do Paulo, 01/09, depois de ouvir o episodio 5: "proibido jogral, proibido
    # comecar uma frase com a palavra dita na fala anterior".
    #
    # O QUE E. A fala seguinte agarra a ultima palavra da anterior e a devolve na
    # abertura, encadeando as vozes pela ponta:
    #   HELENA: a semana ja comecou QUENTE.      DAVI: QUENTE quanto?
    #   HELENA: a mesa finalmente SENTOU.        DAVI: SENTOU ontem?
    #   DAVI: Sentou ONTEM?                      HELENA: ONTEM, as duas e meia.
    # Tres falas presas pela ponta uma na outra. E recitacao escolar, nao conversa.
    #
    # POR QUE A 4b NAO PEGAVA. Aquela so reprova fala que e SUBCONJUNTO da anterior.
    # "Quente quanto?" acrescenta "quanto", entao escapava. Passaram 42 casos no
    # episodio 5, contra ZERO no episodio 1, que o Paulo aprovou.
    #
    # POR QUE SO PALAVRA DE CONTEUDO. Comecar com "E", "Mas", "Entao", "Nao" e fala
    # normal, e barrar isso mataria a conversa em vez de solta-la. O cacoete esta em
    # devolver o SUBSTANTIVO, o verbo, o numero.
    LIGACAO = {"mas", "entao", "porque", "pois", "quando", "como", "que", "quem",
               "isso", "isto", "esse", "essa", "este", "esta", "aquele", "aquela",
               "nao", "sim", "sempre", "ainda", "tambem", "agora", "ali", "aqui",
               "por", "para", "pra", "com", "sem", "sobre", "entre", "desde", "ate",
               "uma", "uns", "umas", "dos", "das", "nos", "nas", "num", "numa",
               "ele", "ela", "eles", "elas", "voce", "gente", "davi", "helena"}
    #
    # SO ENTRE VOZES DIFERENTES. Jogral e alternancia: uma voz devolve a palavra da
    # outra. A mesma voz retomando a propria palavra e enfase, e no episodio 1 aparece
    # em falas que o Paulo aprovou. Medido: sem essa distincao a regra acusava 14 casos
    # no episodio 1, quase todos continuacao do proprio locutor.
    #
    # COMPARA RAIZ, NAO A FORMA EXATA. O Paulo pegou "a mesa sentou" / "sentaram de
    # verdade" numa versao que esta regra tinha aprovado: sao o mesmo verbo em pessoas
    # diferentes, e comparar string com string nao ve isso. Vale para plural tambem
    # ("lance"/"lances"). A raiz e aproximada de proposito: tirar a terminacao pega o
    # cacoete sem precisar de dicionario.
    def raiz(w):
        for suf in ("assem", "essem", "issem", "aremos", "eremos", "iremos",
                    "aram", "eram", "iram", "ando", "endo", "indo",
                    "aria", "eria", "iria", "amos", "emos", "imos",
                    "ados", "adas", "idos", "idas", "ava", "iam",
                    "ado", "ada", "ido", "ida", "ou", "ei", "am",
                    "ar", "er", "ir", "es", "as", "os", "a", "e", "o", "s"):
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                return w[:len(w) - len(suf)]
        return w

    jogral = []
    for i in range(1, len(todas)):
        if quem[i] == quem[i - 1]:
            continue
        seq_b = sequencia(todas[i])
        if not seq_b:
            continue
        primeira = seq_b[0]
        if len(primeira) < 4 or primeira in LIGACAO:
            continue
        if raiz(primeira) in {raiz(w) for w in sequencia(todas[i - 1])}:
            jogral.append((i + 1, primeira, todas[i][:52]))
    for n, palavra, trecho in jogral:
        problemas.append(
            f"JOGRAL na fala {n}: comeca com '{palavra}', que acabou de ser dita na "
            f"fala anterior: '{trecho}'. Reaja ao que foi dito, nao devolva a palavra")

    # ---------- 4d. A ANALISE SEGUE COMPLETA: o Davi nao entra no meio ----------
    # Regra do Paulo, 03/09, ouvindo o episodio 7: "o jogral nao foi eliminado, segue
    # acontecendo. Nem mesmo na pergunta quero que ele devolva. Quero que a analise
    # siga completa."
    #
    # A 4c pegava a palavra devolvida na ponta, e o episodio 7 passou nela com ZERO
    # casos. O jogral tinha mudado de forma: a Helena diz uma frase, o Davi faz uma
    # pergunta de tres palavras ("E o mercado esperava quanto?", "Mirando o que?",
    # "Quais?"), a Helena diz a frase seguinte. A pergunta e deixa, nao pergunta: e a
    # noticia lida a dois, uma frase por vez. Medido no episodio 7: 54 perguntas-deixa
    # do Davi, contra 7 na versao que o Paulo aprovou em 01/09, e o Davi entrando 6 a
    # 10 vezes em cada bloco de analise.
    #
    # A forma que ele quer: em bloco de analise, o Davi CHAMA o lance (no maximo duas
    # falas, antes da primeira da Helena) e sai. A Helena conta a noticia INTEIRA: fato,
    # contexto, impacto, desdobramentos. No fim do bloco o Davi pode voltar com UMA fala
    # (transicao, ou chamar o VAR). Fala dele entre duas falas dela e jogral, com ou sem
    # interrogacao. Unica excecao no meio: a chamada do VAR, assinatura da casa.
    #
    # E o minimo de cinco falas da Helena por bloco existe para que o escritor nao
    # contorne a regra fatiando a noticia em blocos de pergunta e resposta.
    #
    # Blocos de analise sao os BLOCO de numero 2 em diante, menos o FECHO. O 0 e a
    # abertura e o 1 e a escalacao, que sao conversa por desenho.
    #
    # PAPEIS (03/09/2026, a noite): o Paulo ouviu tres testes da mesma reescrita e escolheu
    # a Helena como ancora e o Davi como analista. Os comentarios acima falam do Davi
    # apresentando porque foi assim ate o episodio 8; a regra le HOST e ANALISTA.
    for b in blocos:
        if b["tipo"] != "BLOCO" or b["n"] < 2 or "fecho" in norm(b.get("titulo", "")):
            continue
        quem_b = [q for q, _ in b["falas"]]
        if ANALISTA not in quem_b:
            problemas.append(f"BLOCO {b['n']}: bloco de analise sem nenhuma fala do analista ({ANALISTA})")
            continue
        primeira_h = quem_b.index(ANALISTA)
        if primeira_h > 2:
            problemas.append(
                f"BLOCO {b['n']}: {HOST} abre com {primeira_h} falas antes de {ANALISTA} "
                f"(maximo 2: quem apresenta chama o lance e sai)")
        # REGRA DO PAULO, 04/09/2026, ouvindo o episodio 8: "helena nao faz comentario nenhum
        # no meio das analises do Davi. Ela apenas e a host para chamar as noticias." Entao,
        # a partir da primeira fala do analista, o host so pode aparecer UMA vez: como ultima
        # fala do bloco, dizendo "Chama o VAR!", e so se o bloco seguinte for um bloco VAR.
        # Isso tambem garante o apito: o gerador toca o apito na virada para bloco cujo
        # titulo comeca com VAR; VAR chamado sem esse bloco fica mudo (aconteceu no ep8).
        idx = blocos.index(b)
        prox = blocos[idx + 1] if idx + 1 < len(blocos) else None
        prox_var = prox is not None and prox["tipo"] == "BLOCO" and norm(prox.get("titulo", "")).startswith("var")
        for i, (q, t) in enumerate(b["falas"]):
            if q != HOST or i <= primeira_h:
                continue
            chama = re.search(r"\bvar\b", norm(t)) is not None
            ultima = i == len(b["falas"]) - 1
            if chama and ultima and prox_var:
                continue
            if chama and not prox_var:
                problemas.append(
                    f"BLOCO {b['n']}: chama o VAR mas o bloco seguinte nao e um bloco 'VAR ·': "
                    f"o apito nao toca. O VAR e sempre um bloco proprio, todo do analista")
            elif chama and not ultima:
                problemas.append(
                    f"BLOCO {b['n']}: 'Chama o VAR!' tem de ser a ULTIMA fala do bloco")
            else:
                problemas.append(
                    f"BLOCO {b['n']}: {HOST} fala dentro do lance: '{t[:60]}'. "
                    f"Quem apresenta chama o lance e nao fala mais ate o proximo lance")
        n_analista = quem_b.count(ANALISTA)
        if n_analista < 5:
            problemas.append(
                f"BLOCO {b['n']}: so {n_analista} falas de {ANALISTA} (minimo 5): bloco fatiado "
                f"em pergunta e resposta")

    # O analista tambem nao pode dizer "pede o VAR" e o VAR nao vir: e promessa no ar.
    for idx, b in enumerate(blocos):
        if b["tipo"] != "BLOCO":
            continue
        if any(re.search(r"pede o var", norm(t)) for _, t in b["falas"]):
            prox = blocos[idx + 1] if idx + 1 < len(blocos) else None
            if not (prox is not None and prox["tipo"] == "BLOCO" and norm(prox.get("titulo", "")).startswith("var")):
                problemas.append(
                    f"BLOCO {b['n']}: diz que o ponto pede o VAR, mas o bloco seguinte nao e 'VAR ·'")

    # ESCALACAO (regra do Paulo, 04/09): a Helena faz UMA pergunta ("quais sao os cinco
    # lances de hoje?") e o analista lista; ela nao chama lance por lance.
    esc = next((b for b in blocos if b["tipo"] == "BLOCO" and b["n"] == 1), None)
    if esc:
        hs = [i for i, (q, _) in enumerate(esc["falas"]) if q == HOST]
        if len(hs) > 1 or (hs and hs[0] != 0):
            problemas.append(
                f"BLOCO 1 (escalacao): {HOST} tem {len(hs)} falas. Ela faz uma pergunta so "
                f"('quais sao os cinco lances de hoje?', que pode ficar no fim da abertura) e "
                f"o analista lista os cinco; ela nao chama lance por lance")

    # ---------- 4e. A MESMA VOZ NAO REPETE O QUE ACABOU DE DIZER ----------
    # Paulo, 03/09, ouvindo a reescrita: o Davi fechou a escalacao com "Entao bora!
    # Primeiro lance!" e abriu o bloco seguinte com "Primeiro lance. Helena, ...". Duas
    # falas seguidas da mesma pessoa comecando (ou terminando e recomecando) com as
    # mesmas palavras soam como texto lido, nao como gente falando. As regras 4b e 4c
    # so olham voz DIFERENTE, entao isso passava.
    #
    # O que barra: fala cujas duas primeiras palavras aparecem em sequencia na fala
    # anterior DA MESMA VOZ (valendo atraves da fronteira de bloco, que e onde acontece).
    for i in range(1, len(todas)):
        if quem[i] != quem[i - 1]:
            continue
        a, b = sequencia(todas[i - 1]), sequencia(todas[i])
        if len(a) < 2 or len(b) < 2:
            continue
        # so a EMENDA: a fala anterior termina com as duas palavras com que a nova comeca.
        # Palavra de ligacao nao conta ("o que", "a gente"), e retomar um termo para
        # defini-lo ("...de dia zero." / "Dia zero e a falha que...") e explicacao, nao eco.
        par = (b[0], b[1])
        if par != (a[-2], a[-1]):
            continue
        if b[0] in LIGACAO or b[1] in LIGACAO:
            continue
        if len(b) > 2 and b[2] in ("e", "sao", "era", "significa", "quer"):
            continue
        if True:
            problemas.append(
                f"fala {i + 1}: {quem[i]} repete '{b[0]} {b[1]}', que acabou de dizer na fala "
                f"anterior. A mesma voz nao repete a propria abertura")

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


    # ---------- 8. PISO DE ENERGIA ----------
    # A regra 3 poe TETO no riso porque o exagero incomodou. Faltava o outro lado: o
    # Paulo tambem rejeitou "morno" e "monotono", e um roteiro correto pode ser chato.
    #
    # Calibrado no episodio 1, que ele aprovou: 44% de direcoes energeticas, 57% de
    # falas curtas, 68 caracteres de media. O primeiro roteiro automatico veio com 33%,
    # 49% e 80, e soou monotono. Os pisos ficam entre os dois, mais perto do aprovado.
    #
    # Riso NAO entra aqui: medido, o episodio aprovado tem 1 riso em 168 turnos, igual
    # ao monotono. A energia vem da direcao e do ritmo, nao da risada.
    ENERGICAS = r"excited|amused|energetic|humorous|laugh|surprised"
    if todas:
        tags = [re.match(r"\[([^\]]+)\]", x) for x in todas]
        vivas = sum(1 for m in tags if m and re.search(ENERGICAS, m.group(1), re.I))
        corpos = [len(re.sub(r"\[[^\]]+\]", "", x).strip()) for x in todas]
        curtas = sum(1 for c in corpos if c <= 60)
        media = sum(corpos) / len(corpos)
        if vivas / len(todas) < 0.38:
            problemas.append(
                f"so {vivas/len(todas):.0%} das falas tem direcao energetica "
                f"(piso 38%, o episodio aprovado tem 44%): vai soar monotono")
        if curtas / len(todas) < 0.15:
            problemas.append(
                f"so {curtas/len(todas):.0%} das falas sao curtas o bastante para reagir "
                f"(piso 15%: com o analista narrando, a fala curta e a de chamada e transicao)")
        if media > 135:
            problemas.append(
                f"fala com {media:.0f} caracteres em media (teto 135, uma ideia por fala): "
                f"fala longa demais vira leitura, nao conversa")


    # ---------- 9. DURACAO ALVO ----------
    # O Paulo fixou 15 minutos. A conversao vem da medicao, nao de chute: o episodio 1
    # tem 11.595 caracteres de fala e dura 753s, ou seja 15,4 caracteres por segundo.
    # Faixa larga de proposito: dia de noticia densa pode esticar, e barrar por um minuto
    # seria trocar um problema editorial por um dia sem episodio.
    CHARS_POR_SEG = 15.2
    if todas:
        escrito = sum(len(re.sub(r"\[[^\]]+\]", "", x).strip()) for x in todas)
        seg = escrito / CHARS_POR_SEG
        if not 12 * 60 <= seg <= 18 * 60:
            problemas.append(
                f"episodio de ~{seg/60:.0f} min ({escrito} caracteres de fala). "
                f"O alvo e 15 min, e a faixa aceita vai de 12 a 18")

    # ---------- 6. LASTRO FACTUAL: nada que nao esteja na apuracao ----------
    # O episodio de D comenta as analises publicadas em D-1, porque elas saem as 14h e
    # o programa vai ao ar as 7h da manha seguinte. Buscar a pasta de D acha pasta vazia
    # todo dia, e a regua reprovaria sempre.
    #
    # DOMINGO E DIFERENTE: e apanhado da semana, entao os numeros vem de qualquer dia
    # dos sete anteriores. Conferir so contra a vespera reprovaria tudo que veio de
    # segunda a quinta, ou seja, barraria o formato inteiro.
    alvo_dia = dt.date.fromisoformat(data)
    domingo = alvo_dia.weekday() == 6
    dias = [(alvo_dia - dt.timedelta(days=n)).isoformat()
            for n in (range(1, 8) if domingo else range(1, 2))]
    partes = [c for c in (analises_do_dia(d) for d in dias) if c]
    corpo = "\n".join(partes) if partes else None
    if corpo is None:
        janela = f"os sete dias ate {dias[0]}" if domingo else dias[0]
        problemas.append(f"nao consegui ler as analises de {janela} para conferir os numeros")
    elif domingo and len(partes) < 5:
        # apanhado da semana com dois ou tres dias de apuracao nao e apanhado da semana
        problemas.append(f"apanhado de domingo com apuracao de so {len(partes)} dos 7 dias")
    else:
        # ATUALIZACOES (regra do Paulo, 04/09/2026): as analises sao das 14h da vespera e o
        # roteiro e escrito as 3h do dia do ar. O que mudou no meio (pesquisa da noite,
        # pronunciamento, resposta de quem foi citado) entra numa secao "## ATUALIZACOES"
        # no fim do roteiro, um item por fato, COM URL. Item com URL vale como lastro;
        # item sem URL barra, porque numero sem fonte e exatamente o que esta regra proibe.
        bruto = rascunho.read_text(encoding="utf-8")
        m_at = re.search(r"^## ATUALIZA[^\n]*\n(.*?)(?=^## |\Z)", bruto, re.S | re.M)
        if m_at:
            itens = [l.strip() for l in m_at.group(1).splitlines() if l.strip().startswith("-")]
            for l in itens:
                if "http" not in l:
                    problemas.append(f"ATUALIZACOES: item sem URL nao vale como lastro: '{l[:70]}'")
            corpo = corpo + "\n" + "\n".join(l for l in itens if "http" in l)
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
