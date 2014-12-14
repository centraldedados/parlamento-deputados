#!/bin/sh

# This script
# 1. automatically scraps parlamento's website data
# 2. commits and pushes the data to a github repository

DATAPKG_REPO_URL="git@github.com:publicos_pt/parlamento-deputados.git"
SCRAPER_REPO_URL="git@github.com:publicos_pt/scraper-deputados.git"

SCRAPER_DIR="scraper-deputados"
DATAPKG_DIR="datapkg-deputados"
OUTFILENAME="deputados.csv"
COMMIT_MSG="Automatically updated the list of deputies via scraper."

git pull origin master --force
cd ..
# is the website online?
wget -q --tries=10 --timeout=20 --spider http://www.parlamento.pt
if [ $? -eq 0 ]; then
        echo "Online"
else
        echo "Offline"
fi

if [ ! -d "$DATAPKG_REPO_URL" ]; then
    # clonar repos
    git clone $DATAPKG_REPO_URL $DATAPKG_DIR --quiet
else
    # pull
    cd $DATAPKG_DIR; git pull --quiet; cd ..
fi

# run the script
cd $SCRAPER_DIR
python -m depscrape -f csv -v -p 1 --end 5000 -o ../$OUTFILENAME
cd ..

# if there is no difference, it will not commit anyway.
cd $DATAPKG_DIR && git commit -am "$COMMIT_MSG" && git push
