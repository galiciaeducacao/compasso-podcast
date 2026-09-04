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

Dois apresentadores: **HELENA**, âncora, e **DAVI**, analista. Decisão do paulo em
03/09/2026, ouvindo três versões de teste do mesmo roteiro.

**A Helena só chama.** Ela abre o programa, pergunta os cinco lances, chama cada lance
com uma ou duas falas, lê os três oferecimentos e fecha. **Ela nunca fala dentro de um
lance**: nem pergunta, nem comentário, nem frase de fechamento. Regra do paulo em
04/09/2026, ouvindo o episódio 8: "Helena não faz comentário nenhum no meio das análises
do Davi. Ela apenas é a host para chamar as notícias. Deixa o Davi fazer direto." A única
fala dela dentro de um lance é "Chama o VAR!", como última fala do bloco, quando o Davi
disser que o ponto pede o VAR.

**O Davi conta cada notícia inteira**, do começo ao fim, em cinco passos e nesta ordem:
**o que aconteceu**; **o que é isso** (toda instituição, sigla, lugar e termo explicado na
primeira vez, em meia frase); **por que está acontecendo**; **quem ganha, quem perde e o
que muda para quem ouve**, em coisa concreta, preço, juro, emprego, conta; e **o que vem**,
com data. A audiência é leiga e não é idiota: explicar não é infantilizar.

**A abertura retoma a metodologia em dez segundos**, antes do primeiro lance: depois dos
fixos, a Helena diz em uma fala "do jeito de sempre: o que aconteceu, qual o contexto
geral, por que está acontecendo, quem ganha e quem perde, e quais os possíveis próximos
passos" (redação do paulo, 04/09), e o Davi completa em uma fala "e quando
precisar explicar do zero, a gente chama o VAR". Nada mais didático que isso: uma versão
com cinco falas explicando o formato foi reprovada como "professoral".

**A escalação é uma pergunta só.** A Helena pergunta "quais são os cinco lances de hoje?"
e o Davi lista os cinco, em cinco falas. Ela não chama lance por lance na escalação.

**O VAR é um bloco próprio.** Uma ou duas vezes por episódio, para explicar do zero algo
importante (o que é uma delação, o que é um modelo aberto, o que é um superávit). A
estrutura é obrigatória, porque é ela que faz o apito tocar: o Davi termina um bloco
dizendo que o ponto pede o VAR, a Helena diz "Chama o VAR!" como última fala desse bloco,
e o bloco seguinte tem título começando com `VAR ·` e é todo do Davi. No episódio 8 o
apito só tocou uma vez porque a outra chamada estava no meio de um bloco comum.

**O apito também toca na abertura.** Logo depois de o Davi dizer "a gente para e chama o
VAR", o bloco 0 termina e a linha `> [APITO]` marca o apito; a pergunta da escalação abre
o bloco 1. O gerador só consegue inserir som na fronteira entre blocos, então quem quer o
apito no meio de uma conversa fecha o bloco ali e põe o marcador. E o apito toca a cada
VAR, porque cada VAR é um bloco próprio.

**A vinheta de encerramento** entra sozinha depois da última fala ("Até, Helena!"): o
gerador emenda `audio/vinheta_fim.mp3` no fim da mixagem, e a cama termina nela. Não
precisa marcar nada no roteiro.

**Os cinco passos não são rótulos fixos.** O paulo, revisando o modelo, variou a fórmula:
"o que vem" virou "o que podemos esperar", "o que vem por aí", "o que podemos pensar como
hipótese para o futuro". Acrescentou nuance onde a afirmação era seca ("supostamente",
"ficou claro que", "e que impactam a política global"). Os passos são a ordem do
raciocínio, não cabeçalhos lidos em voz alta; a fala continua sendo de gente conversando.

**Ano se escreve por extenso mesmo** ("em dois mil e vinte e dois", "duas mil e duas
pessoas"): o conferidor de números aprendeu a ler isso em 04/09.

O modelo acabado nessa forma é `roteiros/MODELO.md`, a reescrita do episódio de 04/09
revisada pelo paulo.

## A linguagem

Regra do paulo, 04/09/2026, depois de sete episódios: "Existem muitas frases de efeito,
muitas metáforas, analogias que não dialogam com uma população que não é escolada nisso.
Não é tratar como idiota, é fazer como o The News faz."

**Proibido metáfora, analogia e frase de efeito.** Diga a coisa pelo nome. Saíram, e não
voltam: régua, cartório, guichê, porteiro, pedágio, vitrine, contracampo, moldura,
cobrador, tabuleiro, ficha, praça, árbitro, retrato, idioma, "a mesa sentou", "o barril
cobrou". Um bloco não fecha com sentença ("quem vive de frete não quer guerra grande"):
fecha com o passo quatro ou cinco.

**Vocabulário da casa reduzido a três termos**: escalação, lance e VAR.

**Todo termo explicado na primeira menção**: G20, superávit, protecionismo, Guarda
Revolucionária, Brent, antimicrobiano, delação, relator, modelo aberto. Meia frase basta.

**Falas do Davi curtas**, até cento e vinte caracteres, uma ideia por fala, com direção
diferente em cada uma. O modelo de voz aplica a emoção no ataque e a perde ao longo de
fala longa.

**Bordão em quarentena**: frase que já fechou um episódio não volta por trinta dias.

## O horário: 3h da madrugada, com atualizações

Regra do paulo, 04/09/2026. O episódio 8 disse "o Datafolha sai hoje à noite" quando o
Datafolha tinha saído às 19h da véspera, uma hora depois de o roteiro ser escrito. Então
**o roteiro é escrito às 3h da madrugada do próprio dia do ar**, não na tarde anterior.

| hora (Brasília) | o quê |
|---|---|
| 3h00 | a rotina escreve o rascunho do dia e roda o guardião |
| 3h30 | o guardião roda de novo (3h45 e 4h00 se precisar) |
| 4h00 | gravação (4h15 e 4h30 se precisar) |
| 5h00 | entra no feed |
| 7h00 | hora prometida ao ouvinte |

**A fonte continua sendo as cinco análises da véspera**, publicadas às 14h. Mas o mundo
continuou depois das 14h. Para cada uma das cinco notícias, quem escreve procura na web o
que mudou: pesquisa divulgada à noite, pronunciamento que estava marcado, resposta de quem
foi citado, número revisado, fato novo. Se mudou, o roteiro conta a versão atualizada, e o
fato novo entra numa seção `## ATUALIZAÇÕES` no fim do arquivo, antes de `## FONTES`, um
item por fato, com data, hora e a URL da fonte. **A régua aceita como lastro os números das
análises e os desta seção; item sem URL barra.**

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
    **HELENA:** [warmly] ...

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

Está em "A forma", acima. O histórico dos defeitos que levaram até lá (o jogral de
pergunta-deixa do episódio 5, a Helena comentando no fim de cada bloco no episódio 8)
fica no histórico do repositório e nos comentários das regras 4d e 4e do guardião.

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

**Falta de energia.** Piso de 38% de direções energéticas. Com o Davi narrando, o piso de
falas curtas caiu para 20% e o teto de média subiu para 110 caracteres.

**Helena dentro do lance.** Qualquer fala dela depois da chamada barra, salvo "Chama o
VAR!" como última fala antes de um bloco `VAR ·`.

**VAR sem bloco.** "Pede o VAR" ou "Chama o VAR" sem bloco `VAR ·` logo depois barra:
o apito não tocaria.

**Atualização sem fonte.** Item de `## ATUALIZAÇÕES` sem URL barra.

## Pronúncia

As trocas de pronúncia ficam em `scripts/lexico_pronuncia.json` e são aplicadas sozinhas:
o roteiro fica legível para humano. **Não escreva pronúncia no roteiro.** Se descobrir uma
palavra saindo errada no ar, a correção vai para o léxico.

Duas armadilhas já pagas: nunca use maiúscula em palavra curta para forçar sigla, e nunca
insira vírgula para ajudar a soletrar, porque vírgula é pausa.

## Depois de escrever

O rascunho fica em `roteiros/rascunhos/`. **Um arquivo nesta pasta não vai ao ar.** Quem
promove é o guardião, às 3h30, e só se tudo passar. Se ele barrar, abre uma issue dizendo
o motivo, e ninguém fica sabendo tarde demais.
