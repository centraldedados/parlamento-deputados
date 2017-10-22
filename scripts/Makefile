install:
	virtualenv .env --no-site-packages --distribute --prompt=\(scraper-deputados\)
	. `pwd`/.env/bin/activate; pip install -r requirements.txt

scrape:
	. `pwd`/.env/bin/activate; python scrape.py --to-csv --to-json
	mv -f deputados.csv deputados.json ../data
