parlamento-deputados
====================

TODO

Receitas
--------

Para descarregar todas as fotos dos deputados a partir do parlamento.pt na linha de comandos, com o `jq`, `xargs` e `wget`:

    cat deputados.json | jq '.[] | .image_url,.slug' | sed 's/"//g' | xargs -L 2 sh -c 'wget $1 -O $2.jpg' argv0
