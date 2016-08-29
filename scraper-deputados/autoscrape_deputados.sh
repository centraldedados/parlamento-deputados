#!/bin/sh

set -e # exits at any error

# This script
# 1. automatically scraps parlamento's website data
# 2. commits and pushes the data to a github repository

DATAPKG_REPO_URL="git@github.com:centraldedados/parlamento-deputados.git"
SCRAPER_REPO_URL="git@github.com:transparenciahackday/scraper-deputados.git"

SCRAPER_DIR="scraper-deputados"
DATAPKG_DIR="datapkg-deputados"
OUTFILENAME="deputados.csv"
COMMIT_MSG="Automatically updated the list of deputies via scraper."

echo "Updating source code..."
git pull origin master --force
cd ..

if [ ! -d "$DATAPKG_DIR" ]; then
    # clone data repositiory
    git clone $DATAPKG_REPO_URL $DATAPKG_DIR --quiet
else
    echo "Updating data repositiory..."
    cd $DATAPKG_DIR; git pull origin master --quiet --force; cd ..
fi

echo "Running the scraper..."
cd $SCRAPER_DIR
python2.7 -m depscrape -f csv -v -p 1 --end 5000 -o ../$OUTFILENAME
cd ..

# FIXME: csvsort

# if there is no difference, it will not commit anyway.
echo "Comparing changes and committing if needed..."
cp $OUTFILENAME $DATAPKG_DIR/data -f
cd $DATAPKG_DIR && git commit -am "$COMMIT_MSG" && git push
