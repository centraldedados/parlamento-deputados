install:
	virtualenv .env --no-site-packages --distribute --prompt=\(scraper-deputados\)
	. `pwd`/.env/bin/activate; pip install -r requirements.txt

scrape:
	python scrape.py --format csv
	csvsort deputados.csv -c id > deputados-sorted.csv
	mv -f deputados-sorted.csv ../data/deputados.csv
	rm -f deputados.csv
	python scrape.py --format json
	mv -f deputados.json ../data
