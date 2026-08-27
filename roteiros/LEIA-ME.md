# Roteiros

Um arquivo por episódio, com o nome no formato `AAAA-MM-DD.md`, na data em que o
episódio vai ao ar.

**A presença do arquivo é a aprovação.** O workflow das 18h procura o roteiro da data
de amanhã. Se não existir, ele sai sem fazer nada, e isso não é erro: é o jeito de
segurar um dia sem precisar desligar nada.

O roteiro precisa ter os blocos marcados assim, que é o que o gerador reconhece:

    ## [BLOCO 0] ABERTURA
    **DAVI:** [very excited] ...
    **HELENA:** [warmly] ...

    ## [ANUNCIO 1] LEGALE
    **DAVI:** [excited] ...

Os `[ANUNCIO 1]`, `[2]` e `[3]` recebem automaticamente o sonic logo da Legale, da
Iure Digital e da Galícia, nessa ordem, com a trilha cortada na assinatura e bem
baixa sob a locução.

Para o título e o resumo do episódio no feed, o roteiro pode trazer:

    # Título curto do episódio
    > RESUMO: uma frase que aparece na descrição do episódio nos tocadores.
