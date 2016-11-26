Este scraper vai buscar as páginas de deputados do Parlamento.pt e extrai uma parte da informação, convertendo para JSON ou CSV. 

O que é gravado no registo de cada deputado:
  * Nome completo
  * Nome abreviado
  * Data de nascimento
  * Profissão
  * Comissões parlamentares de que faz parte
  * Condecorações
  * URL da fotografia atual
  * Se está atualmente na AR
  * URL do deputado/a no Parlamento.pt
  * URL do deputado/a no Demo.cratica

A versão JSON inclui também a lista de mandatos para cada deputado. Em cada mandato é especificado:
  * número da legislatura
  * data de início do mandato
  * data de fim do mandato
  * círculo eleitoral por que foi eleito/a
  * partido por que foi eleito/a
  * o URL da página de atividade parlamentar
  * o URL da página de registo de interesses (quando disponível)

O que ainda não está coberto:
  * conteúdo dos registos de interesses
  * conteúdo das páginas de atividade parlamentar
  * links para registos de interesses com imagens
  * URLs das videobiografias
  * registos de presenças

## Preparação

Para instalar as dependências necessárias em Debian GNU/Linux:

    sudo apt-get install python-dev libxml2-dev libxslt-dev

Depois, para instalar o virtualenv, já no diretório base do repositório:

    cd scripts
    make install


## Como usar

Para atualizar os datasets no diretório `data/`:
    make scrape

### Correr o script diretamente

Gravar o resultado num ficheiro JSON:
    python scrape.py -o deputados.json

Gravar o resultado num ficheiro JSON com uma indentação de 4 espaços:
    python scrape.py -o deputados.json -i 4

Gravar o resultado num ficheiro CSV:
    python scrape.py -f csv -o deputados.csv

Para ver todas as opções possíveis:
    python scrape.py --help

