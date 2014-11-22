#!/bin/sh

# bot para scrape e push dos deputados

DATAPKG_REPO_URL="git@github.com:centraldedados/parlamento-deputados.git"
SCRAPER_REPO_URL="git@github.com:transparenciahackday/scraper-deputados.git"
SCRAPER_SCRIPT="depscrap -f csv -v -p 1 -o ../deputados.csv"

SCRAPER_DIR="scraper-deputados"
DATAPKG_DIR="datapkg-deputados"
OUTFILENAME="deputados.csv"
COMMIT_MSG="Auto update"

# site está online?
wget -q --tries=10 --timeout=20 --spider http://www.parlamento.pt
if [ $? -eq 0 ]; then
        echo "Online"
else
        echo "Offline"
fi

if [ ! -d "$SCRAPER_DIR" ]; then
    # clonar repos
    git clone $SCRAPER_REPO_URL $SCRAPER_DIR --quiet
    git clone $DATAPKG_REPO_URL $DATAPKG_DIR --quiet
else
    # pull
    cd $SCRAPER_DIR; git pull --quiet; cd ..
    cd $DATAPKG_DIR; git pull --quiet; cd ..
fi


# commit e push se os ficheiros forem diferentes
# src: http://stackoverflow.com/questions/12900538/unix-fastest-way-to-tell-if-two-files-are-the-same
cd $SCRAPER_DIR && ./$SCRAPER_SCRIPT && cd .. && \
cmp --silent $OUTFILENAME $DATAPKG_DIR/data/$OUTFILENAME || \
  cp $OUTFILENAME $DATAPKG_DIR/data -f && \
  cd $DATAPKG_DIR && git commit -am "$COMMIT_MSG" && git push && \
  cd ..
