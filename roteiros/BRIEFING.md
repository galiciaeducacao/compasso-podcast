# Como escrever um episódio do COMPASSO CAPITAL

Este documento é a instrução de trabalho de quem escreve o roteiro diário, seja pessoa
ou rotina automática. O modelo acabado é `roteiros/2026-08-28.md`, o episódio 1: quando
este texto e aquele arquivo discordarem, **o arquivo manda**, porque foi ao ar.

## A fonte, e só ela

As cinco análises publicadas em **compasso.capital** no dia anterior. Elas ficam em
`galiciaeducacao/claude-galicia`, em `galicia/compasso/ops/diarias/<AAAA-MM-DD>/`, um
JSON por pilar.

Nada entra no episódio que não esteja nelas. **Nenhum número dito no ar pode faltar na
apuração do dia**, e a régua confere isso sozinha. Não vale completar de memória, não
vale buscar em outro lugar, não vale arredondar para soar melhor.

O episódio sempre manda o ouvinte ao site para o detalhamento.

## A regra temporal, que é onde todo mundo erra

A análise é da **véspera** e o programa vai ao ar às 7h do dia seguinte. Então o texto
nasce dizendo "hoje" sobre um fato de ontem, e isso precisa ser convertido:

| o que é | como se fala |
|---|---|
| fato ocorrido na véspera | **ontem** |
| agenda do próprio dia do ar | **hoje** |
| referência ao programa | **hoje** ("a escalação de hoje") |

O erro é invisível para quem escreve, porque na hora de escrever era mesmo hoje. A régua
barra o rascunho se pegar "hoje" colado a verbo no passado.

## A forma

Dois apresentadores: **DAVI**, âncora que conduz por perguntas, e **HELENA**, analista.

Cada notícia abre em quatro tempos, nesta ordem: **o fato**, **o contexto** em que ele se
encaixa, **o impacto** (quem ganha e quem perde) e os **desdobramentos**. Fecha com **onde
você está nesse lance**, que é o que o ouvinte faz com aquilo.

A audiência não quer saber o que é economia política. Quer o fato, o contexto, os impactos
e o que pode vir. Explicar não é infantilizar.

### O vocabulário da casa

O programa fala em **jogo**, e só três termos sustentam isso, para não virar programa
esportivo: **a escalação** abre o episódio, com a lista dos lances do dia; **próximo lance**
marca cada virada de bloco; **o VAR** é a assinatura analítica e só aparece onde há
reviravolta de verdade.

Fixos que repetem sempre: "bom dia, viventes", "esfera de confusão", "sete da manhã, café
na mão", "no jogo do excedente / ninguém assiste de fora", "onde você está nesse lance",
e o fecho "o jogo não para, amanhã a gente volta".

### Os oferecimentos

Três blocos `[ANUNCIO 1|2|3]`, um por marca, **sempre as três, em ordem rotativa**:
Legale Educacional, Iure Digital, Galícia Educação. Cada uma assina uma notícia.

## O formato do arquivo

`roteiros/rascunhos/<AAAA-MM-DD>.md`, com a data **do ar**, não a da apuração.

    # Título curto do episódio
    > RESUMO: uma frase, que vira a descrição nos tocadores.

    ## [BLOCO 0] ABERTURA
    **DAVI:** [very excited] ...
    **HELENA:** [warmly] ...

    ## [ANUNCIO 1] LEGALE
    **DAVI:** [warmly] ...

Toda fala começa com uma tag de direção entre colchetes. Fala sem direção é onde o modelo
mais varia sozinho.

## O que a régua barra (`scripts/guardiao.py`)

Vale ler os motivos, não só a lista: cada um veio de um defeito que foi ao ar.

**Bloco que não cabe numa chamada.** O limite não é o tamanho do bloco: é o bloco **mais a
última fala do bloco anterior**, que o gerador cola na frente para manter a continuidade.
Soma acima de 1900 caracteres parte o bloco em duas chamadas, e a emenda interna nasce sem
continuidade. Morde mais depois dos anúncios, porque o texto do oferecimento é uma fala
longa. Escreva blocos de 1200 a 1500 caracteres e isso nunca acontece.

**Número em algarismo.** Escrever por extenso, sempre. O modelo lê algarismo de formas
imprevisíveis.

**Maiúscula em palavra curta.** O modelo lê como sigla. Ênfase se faz com a tag, não com
caixa alta.

**Riso.** Teto de 15% dos turnos, nunca em turnos seguidos, e quem conta a piada não ri
da própria piada.

**Eco.** Fala que devolve o que a outra acabou de dizer. Cinco palavras seguidas repetidas
da fala anterior já barram. Reagir é acrescentar, não repetir.

**Número sem lastro.** Ver acima.

## Pronúncia

As trocas de pronúncia ficam em `scripts/lexico_pronuncia.json` e são aplicadas sozinhas:
o roteiro fica legível para humano. **Não escreva pronúncia no roteiro.** Se descobrir uma
palavra saindo errada no ar, a correção vai para o léxico.

Duas armadilhas já pagas: nunca use maiúscula em palavra curta para forçar sigla, e nunca
insira vírgula para ajudar a soletrar, porque vírgula é pausa.

## Depois de escrever

O rascunho fica em `roteiros/rascunhos/`. **Um arquivo nesta pasta não vai ao ar.** Quem
promove é o guardião, às 17h, e só se tudo passar. Se ele barrar, abre uma issue dizendo
o motivo, e ninguém fica sabendo tarde demais.
