# Testa o localizador de corte do priming contra os modos de falha conhecidos.
# Nao chama API: substitui a transcricao por uma lista de palavras com tempo.
#
# O corte correto e SEMPRE o indice da primeira palavra da fala nova na transcricao,
# menos a margem de respiro.
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import gerar_episodio as g

PASSO = 0.30  # cada palavra dura 0,3s, o suficiente para o teste


def transcricao(frase):
    return [{"text": p, "start": i * PASSO, "end": (i + 1) * PASSO}
            for i, p in enumerate(frase.split())]


def rodar(nome, dito, contexto, primeira, esperado):
    g.palavras_com_tempo = lambda _arq: transcricao(dito)
    r = g.inicio_do_bloco("ignorado", contexto, primeira)
    if esperado is None:
        ok, alvo = r is None, "abortar"
        obtido = "abortou" if r is None else f"cortou em {r:.2f}s"
    else:
        ideal = max(0.0, esperado * PASSO - 0.12)
        ok = r is not None and abs(r - ideal) < 0.001
        alvo = f"{ideal:.2f}s (palavra {esperado}: '{dito.split()[esperado]}')"
        obtido = "abortou" if r is None else f"{r:.2f}s"
    print(f"[{'ok    ' if ok else 'FALHOU'}] {nome}")
    if not ok:
        print(f"           esperado {alvo}, obtido {obtido}")
    return ok


CTX = "a analise completa esta no nosso site compasso ponto capital"
tudo = []

# 1. caso normal: as primeiras palavras da fala nova casam em sequencia
tudo.append(rodar(
    "ancora completa",
    CTX + " proximo lance a china pediu ontem",
    CTX, "[curious] Proximo lance: a China pediu ontem", 10))

# 2. o bug original: a transcricao colou o endereco do site numa palavra so.
# Ancorar no FIM do contexto falharia aqui; ancorar no INICIO da fala nova, nao.
tudo.append(rodar(
    "contexto termina em endereco colado",
    "a analise completa esta no nosso site compasso.capital proximo lance a china pediu",
    CTX, "[curious] Proximo lance: a China pediu", 8))

# 3. a transcricao errou o comeco da fala nova; salva pela palavra distintiva,
# com recuo pelo indice ate o comeco real
tudo.append(rodar(
    "queda pela palavra distintiva, com recuo",
    CTX + " proximos lances a nvidia dobrou a receita",
    CTX, "[serious] Proximo lance: a Nvidia dobrou a receita", 10))

# 4. A ARMADILHA DO INDICE NEGATIVO: a distintiva ('nvidia', 6a da fala nova) tambem
# aparece ANTES, no meio do contexto. Sem comecar a busca em max(piso, idx), o recuo
# daria 4-6 = -2, que em Python da a volta na lista sem erro nenhum e corta num ponto
# aleatorio do audio.
tudo.append(rodar(
    "distintiva aparece antes: nao pode virar indice negativo",
    "bom dia agora vamos nvidia sobre isso eh agora vamos falar sobre a nvidia dobrou",
    "bom dia agora vamos falar sobre isso",
    "[serious] E agora vamos falar sobre a Nvidia, dobrou", 7))

# 5. nada casa: tem de abortar, nunca chutar
tudo.append(rodar(
    "nada casa, aborta",
    CTX + " conteudo totalmente diferente do que foi escrito",
    CTX, "[warmly] Isso muda o jogo inteiro para quem exporta", None))

# 6. ultima queda: nenhuma palavra distintiva (todas curtas ou ja no contexto),
# mas a primeira palavra da fala nova aparece uma unica vez na regiao
CTX2 = "isso e o que voce faz com a nossa analise"
tudo.append(rodar(
    "ultima queda com primeira palavra unica",
    CTX2 + " mas isso eh o que voce faz",
    CTX2, "[amused] Mas isso e o que voce faz", 10))

# 7. mesma situacao, mas a primeira palavra se repete: escolher uma seria sorteio,
# entao aborta
tudo.append(rodar(
    "primeira palavra repetida: aborta em vez de sortear",
    CTX2 + " mas isso eh o que voce faz mas de novo",
    CTX2, "[amused] Mas isso e o que voce faz", None))

# 8. a margem de respiro nunca pode produzir tempo negativo
tudo.append(rodar(
    "corte no inicio absoluto nao vira tempo negativo",
    "proximo lance a china pediu", "", "[curious] Proximo lance: a China pediu", 0))

print("\n" + ("todos passaram" if all(tudo) else "HA FALHA ACIMA"))
sys.exit(0 if all(tudo) else 1)
