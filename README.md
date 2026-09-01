# COMPASSO CAPITAL

Feed e arquivos do podcast diário do COMPASSO CAPITAL.

**O podcast que traduz os interesses nas entrelinhas das notícias.**
Todos os dias, às 7 da manhã. Porque no jogo do excedente, ninguém assiste de fora.

- Feed RSS: `https://galiciaeducacao.github.io/compasso-podcast/feed.xml`
- Análises completas: [compasso.capital](https://compasso.capital)
- Contato: contato@compasso.capital

## Onde fica o áudio

Em dois lugares, com papéis diferentes:

- **Cloudflare R2**, em `audio.compasso.capital` — é quem **serve** o episódio. Foi para
  lá porque o *release* do GitHub entrega o mp3 como `application/octet-stream`, com
  `Content-Disposition: attachment` e numa URL assinada que expira em uma hora: isso manda
  o aparelho **baixar** em vez de **tocar**, e a Apple recusava o episódio por causa disso.
- ***Releases* do GitHub**, um por episódio — é quem **guarda**. Não conta em cota nenhuma,
  e é o que permite a faxina semanal apagar episódio velho do R2 sem perder nada.

O balde fica dentro da faixa gratuita (10 GB) por `scripts/limpar_r2.py`, que roda aos
domingos: mantém os 180 episódios mais recentes servidos (~3,8 GB) e tira do balde e do
feed os anteriores, só depois de confirmar que o *release* responde. Para ver a conta:
`python scripts/limpar_r2.py --conferir`.

Este repositório é público porque os agregadores (Spotify, Apple, YouTube Music) baixam
os arquivos sem autenticação.
