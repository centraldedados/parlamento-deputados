install:
	virtualenv .env --no-site-packages --distribute --prompt=\(scraper-deputados\)
	. `pwd`/.env/bin/activate; pip install -r requirements.txt

scrape:
	. `pwd`/.env/bin/activate; python scrape.py --format csv
	mv -f deputados.csv ../data
	. `pwd`/.env/bin/activate; python scrape.py --format json
	mv -f deputados.json ../data
