# Rascunhos

Quem escreve, escreve **aqui**. Um arquivo por episódio, `AAAA-MM-DD.md`.

Um roteiro nesta pasta **não vai ao ar**. O workflow das 18h olha apenas a pasta
`roteiros/`, um nível acima, e ignora esta.

## Aprovar é mover

    git mv roteiros/rascunhos/2026-08-28.md roteiros/2026-08-28.md

É esse movimento, e só ele, que autoriza a gravação. Fica registrado no histórico
do repositório: dá para saber quem aprovou o quê e quando.

## Por que não basta "o arquivo existe"

A convenção anterior era que a presença de `roteiros/<data>.md` valia como aprovação.
Isso funciona enquanto só gente cria o arquivo. No dia em que uma rotina automática
escrever e enviar, o arquivo passaria a existir sem ninguém ter lido, e a trava viraria
carimbo. Pior: a falha seria silenciosa, porque do ponto de vista do workflow estaria
tudo certo.

Com duas pastas, escrever e aprovar são atos separados, e o segundo continua sendo humano
mesmo quando o primeiro deixar de ser.

## A regra temporal: quem fala é a manhã seguinte

A fonte de um episódio é **sempre a análise da véspera**, porque as análises saem às
14h e o programa vai ao ar às 7h do dia seguinte. Então o texto nasce naturalmente
dizendo "hoje" sobre um fato de ontem, e isso precisa ser convertido antes de subir:

| o que é | como se fala |
|---|---|
| fato ocorrido na véspera | **ontem** ("o IBGE divulgou ontem") |
| agenda do próprio dia do ar | **hoje** ("e hoje, daqui a pouco, o discurso em Jackson Hole") |
| referência ao programa | **hoje** ("me dá a escalação de hoje") |

Um matinal que chama de "hoje" o que aconteceu ontem perde credibilidade rápido, e o
erro é invisível para quem escreveu, porque na hora de escrever era mesmo hoje. Por
isso a régua confere sozinha (regra 7 do `guardiao.py`) e barra o rascunho.

O ganho não é só de correção: separar o que passou do que está por vir transforma um
retrospecto em programa com **agenda do dia**, que é o que se espera de um matinal.
