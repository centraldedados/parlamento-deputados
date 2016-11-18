install:
	virtualenv .env --no-site-packages --distribute --prompt=\(scraper-deputados\)
	. `pwd`/.env/bin/activate; pip install -r requirements.txt

scrape:
	python scrape.py --format json
	mv -f deputados.json ../data
	python scrape.py --format csv
	mv -f deputados.csv ../data
