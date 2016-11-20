install:
	virtualenv .env --no-site-packages --distribute --prompt=\(scraper-deputados\)
	. `pwd`/.env/bin/activate; pip install -r requirements.txt

scrape:
	. `pwd`/.env/bin/activate; python scrape.py --format csv
	. `pwd`/.env/bin/activate; csvsort deputados.csv -c id > deputados-sorted.csv
	mv -f deputados-sorted.csv ../data/deputados.csv
	rm -f deputados.csv
	. `pwd`/.env/bin/activate; python scrape.py --format json
	mv -f deputados.json ../data
