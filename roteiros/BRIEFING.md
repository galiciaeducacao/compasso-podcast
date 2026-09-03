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

### O balanço do mês NÃO entra no podcast

Regra do paulo, 01/09/2026. **No dia 1º de cada mês a rotina do site publica as MENSAIS
em vez das diárias**, cobrindo o mês que terminou. O podcast NÃO comenta essas.

Aconteceu em 01/09: o roteiro do dia 2 nasceu abrindo com "o mês em que a ameaça virou
tabela de preços", um fechamento de agosto, no dia em que o Brasil tinha saído o PIB, uma
decisão do ministro Alexandre de Moraes e a liberação de recurso para Flávio Bolsonaro. O
paulo vetou na leitura: **programa diário não abre com balanço do mês.** A régua tinha
aprovado, porque o roteiro era fiel à fonte; o defeito estava na fonte do dia, não no
texto.

**O que fazer quando a pasta do dia só tiver mensais:** não escreva o episódio com elas.
Avise no resumo final, com todas as letras, que a apuração do dia é mensal e que o
episódio depende de uma rodada diária. Um dia sem episódio é problema conhecido; um
matinal comentando o mês passado é problema que o ouvinte percebe.

O podcast acompanha a análise **diária** e, no domingo, a **semanal**. Nunca a mensal.

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

## O domingo é diferente: apanhado da semana

De segunda a sábado o episódio comenta as cinco análises da véspera, uma notícia por
pilar. **No domingo, não.** O domingo é a síntese do que o COMPASSO noticiou na semana
inteira, de segunda a sábado.

Os lances do domingo levam **o nome dos pilares**, não o da notícia. Em vez de "o estreito
aberto por declaração", o lance é o pilar, e dentro dele se conta o que a semana mostrou:
o que começou, o que virou, e o que ficou de pé para a semana seguinte.

Isso muda o que a régua confere. Nos outros dias, todo número tem de existir na apuração
da véspera; **no domingo, em qualquer dia dos sete anteriores**. Ela também exige apuração
de pelo menos cinco dos sete dias, porque apanhado de semana feito com dois dias de
material não é apanhado de semana.

O tom não muda: continua leve, com os mesmos pisos de energia, a mesma duração alvo, os
mesmos três oferecimentos e o mesmo vocabulário da casa. O que muda é o recorte, que
passa de vinte e quatro horas para sete dias.

E a regra temporal fica mais fácil, não mais difícil: no domingo se fala em dias da
semana ("na quarta", "na sexta") em vez de "ontem", porque o material é de vários dias.

## A forma

Dois apresentadores: **DAVI**, âncora que chama os lances, e **HELENA**, analista, que conta cada notícia inteira.

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

## O ritmo, que é onde o primeiro roteiro automático escorregou

Um roteiro pode estar todo certo e ainda assim ser chato. O paulo rejeitou os dois
extremos: o riso exagerado, e o programa "morno" e "monótono". A régua tem teto de riso
desde o começo; o piso de energia entrou depois, quando o primeiro roteiro automático
saiu correto e sem vida.

Os números vêm do episódio 1, que ele aprovou, comparado com o que soou monótono:

| | aprovado | monótono | piso da régua |
|---|---|---|---|
| falas com direção energética | 44% | 33% | **38%** |
| falas curtas, até 60 caracteres | 57% | 49% | **52%** |
| tamanho médio da fala | 68 | 80 | **teto 74** |

Direção energética é `[excited]`, `[very excited]`, `[amused]`, `[energetic]`,
`[surprised]`, e as de riso. As calmas, `[warmly]`, `[thoughtful]`, `[serious]`,
`[curious]`, existem para contraste, não para preencher.

**Riso não é o que dá vida.** Medido: o episódio aprovado tem uma risada em 168 turnos,
exatamente a mesma proporção do que soou monótono. A energia vem da **direção** e do
**contraste**, não da risada nem da troca de voz.

O que torna um trecho vivo é a fala curta, uma embaixo da outra, com direção diferente
em cada uma. Fala longa vira leitura em voz alta. Se um raciocínio precisa de cinco linhas,
quebre em várias falas **da mesma voz**, uma embaixo da outra.

**Quebrar em falas não é alternar.** Esta frase, na versão anterior deste briefing,
mandava quebrar "com o outro reagindo no meio", e foi ela que produziu o pior defeito que
o programa já teve no ar.

### Quem fala o quê

**O Davi apresenta. A Helena analisa, e a análise segue completa.**

Regra do paulo, 03/09/2026, ouvindo o episódio 7: "o jogral não foi eliminado, segue
acontecendo. Nem mesmo na pergunta quero que ele devolva. Quero que a análise siga
completa."

O que tinha acontecido: a régua do jogral (regra 4c) pegava a palavra devolvida na ponta,
e o episódio 7 passou nela com zero casos. Mas o jogral tinha mudado de forma. A Helena
dizia uma frase, o Davi fazia uma pergunta de três palavras, a Helena dizia a frase
seguinte:

    HELENA: Às nove, o IBGE mostrou a produção industrial de julho.
    HELENA: Cresceu zero vírgula dois por cento sobre junho.
    DAVI: E o mercado esperava quanto?
    HELENA: Zero vírgula cinco. Veio abaixo.
    DAVI: E contra o ano passado?
    HELENA: Recuo de zero vírgula cinco por cento.

A pergunta é deixa, não pergunta. É a notícia lida a dois, uma frase por vez. Medido no
episódio 7: cinquenta e quatro perguntas-deixa do Davi, e ele entrando de seis a dez
vezes em cada bloco de análise.

A forma que vale a partir do episódio de 04/09:

1. **O Davi chama o lance** em no máximo duas falas, antes da primeira fala da Helena.
   A chamada pode ser uma pergunta que abre a análise ("Helena, por que uma fila em
   Xangai interessa à mesa com Washington?"). Depois ele **sai**.
2. **A Helena conta a notícia inteira**: fato, contexto, impacto, desdobramentos. Em
   falas curtas dela mesma, uma embaixo da outra, cinco no mínimo por bloco. Ninguém
   entra no meio: nem pergunta, nem comentário, nem reação de uma palavra.
3. **No fim do bloco** o Davi pode voltar com **uma** fala: a transição para o próximo
   lance, ou a chamada do VAR. A chamada do VAR é a única fala dele que pode aparecer
   no meio de um bloco.

O mesmo trecho, na forma certa:

    DAVI: Quarto lance! O Brasil, com dois retratos no mesmo dia. Helena, começa pela manhã.
    HELENA: Às nove, o IBGE mostrou a produção industrial de julho.
    HELENA: Cresceu zero vírgula dois por cento sobre junho, quando o mercado esperava zero vírgula cinco.
    HELENA: Contra julho do ano passado, recuo de zero vírgula cinco.
    HELENA: E julho tem um agravante de calendário: foi o primeiro mês inteiro sob a tarifa americana cheia.
    HELENA: Vinte e cinco por cento pela lei comercial, mais a sobretaxa de doze vírgula cinco.
    HELENA: Então o custo já apareceu no dado. E apareceu onde o PIB de terça não deixava ver.
    HELENA: O agregado cresce pelo campo e pela mina. A transformação, que é onde a tarifa morde, anda de lado.
    DAVI: E à tarde, o outro retrato.

A energia da Helena vem da direção e do contraste entre as falas dela, não de alguém
cutucando no meio. Os blocos 0 (abertura) e 1 (escalação) continuam sendo conversa, e
o fecho também. A régua (regra 4d) confere todos os blocos de análise: fala do Davi
entre duas falas da Helena barra o rascunho, e bloco com menos de cinco falas dela
também, para que ninguém contorne a regra fatiando a notícia em blocos pequenos.

**Não use os roteiros de 28/08 a 03/09 como modelo de quem fala.** Todos têm o defeito,
inclusive a versão aprovada em 01/09, que ainda tinha o Davi perguntando no meio. O
modelo é o exemplo acima.

**Clareza vem antes de tudo.** Duas frases foram reprovadas na leitura do episódio 5, e
nenhuma régua pega esse tipo de defeito:

- *"hoje tem número nosso também"*: o ouvinte não tem como saber que "número" é o PIB,
  que ainda nem foi mencionado. Virou "hoje sai o número da economia brasileira".
- *"a mesa do tarifaço sentou"*: mesa não senta. Metonímia que não fecha soa como erro.
  Virou "a negociação do tarifaço começou".

Isso não tem a ver com o tamanho do episódio. Um episódio de dezessete minutos pode ser
vivo, e um de dez pode ser monótono.

### A duração e o tom

**O alvo é quinze minutos.** A conversão é medida, não estimada: **15,2 caracteres de
fala por segundo**, sem contar as tags de direção, que ninguém fala. Então quinze minutos
são cerca de **13.700 caracteres**. A régua aceita de doze a dezoito minutos, faixa larga
de propósito, porque dia de notícia densa pode esticar e barrar por um minuto seria trocar
um problema editorial por um dia sem episódio.

E o tom: **leve, algo gostoso de ouvir pela manhã.** Isso não é o mesmo que raso. O
assunto continua sendo disputa por excedente, embargo e juro. Leve é o jeito: frase curta,
gente conversando de verdade, um respiro de humor onde couber, nenhuma frase que precise
ser relida. Se um trecho soa como alguém lendo relatório em voz alta, ele está errado,
mesmo que cada palavra esteja certa.

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

**Eco curto**, que é o mais comum e o mais irritante. Duas coisas distintas:

*Repetição idêntica nunca presta*, de qualquer tamanho. "Antes do almoço?" seguido de
"Antes do almoço." não é reação, é devolver a frase. O episódio aprovado não tem nenhuma.

*Eco que condensa é recurso legítimo*, e bom: "Nenhum dólar? Da China inteira?" seguido de
"Nenhum." O problema é a dose. O aprovado tem dois em 168 falas, 1%. O primeiro roteiro
automático veio com onze em 219, 5%, e vira cacoete mesmo quando cada um passaria sozinho.
Teto de 3%.

Quando a vontade for ecoar, acrescente em vez de devolver. No lugar de "Antes do almoço.",
diga o que aquilo significa.

**Número sem lastro.** Ver acima.

**Falta de energia.** Ver a seção do ritmo: pisos de 38% de direções energéticas e 52%
de falas curtas, e teto de 74 caracteres de média por fala.

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
