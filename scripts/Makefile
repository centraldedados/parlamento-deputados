scrape:
	./extract.py
	mv -f deputados.csv ../data
	mv -f deputados.json ../data
	
install:
	virtualenv .env --python=/usr/bin/python3 --no-site-packages --distribute
	. `pwd`/.env/bin/activate; pip install -r requirements.txt

deploy:
	git add ../data/
	git commit -m "Atualização automática"
	git push origin master
