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
