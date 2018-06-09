Este dataset contém informação dos deputados extraída do Parlamento.pt.

[![goodtables.io](https://goodtables.io/badge/github/centraldedados/parlamento-deputados.svg)](https://goodtables.io/github/centraldedados/parlamento-deputados)

Importa notar que a versão JSON dos dados contém mais campos que o CSV não tem:

* `mandates` -- informação sobre cada mandato individual
* `jobs` -- cargos ocupados no passado
* `current_jobs` -- cargos ocupados no presente

A documentação do scraper (descrita abaixo) contém mais informação sobre os dados e a sua disposição..

## Scraper

Os pormenores sobre o scraper que usamos para extrair os dados do Parlamento.pt está documentado [no seu diretório](https://github.com/centraldedados/parlamento-deputados/blob/master/scripts/README.md).


Receitas
--------

Para descarregar todas as fotos dos deputados a partir do parlamento.pt na linha de comandos, com o `jq`, `xargs` e `wget`:

    cat deputados.json | jq '.[] | .image_url,.slug' | sed 's/"//g' | xargs -L 2 sh -c 'wget $1 -O $2.jpg' argv0
