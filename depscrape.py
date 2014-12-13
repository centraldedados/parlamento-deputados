#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hashlib import sha1
import os
import urllib
import shutil
from bs4 import BeautifulSoup
import re
from itertools import chain
from datetime import datetime as dt
from json import dumps
import codecs
import csv
from replaces_depscrap import SHORTNAME_REPLACES
import click
from zenlog import log
import multiprocessing


fieldnames = ['id', 'shortname', 'name', 'party', 'active', 'education', 'birthdate', 'occupation', 'current_jobs',
              'jobs', 'commissions', 'mandates', 'awards', 'url', 'scrape_date']

DEFAULT_MAX = 5000

ROMAN_NUMERALS = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
                  'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
                  'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
                  'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
                  'XXI': 21, 'XXII': 22, 'XXIII': 23, 'XXIV': 24, 'XXV': 25}

URL_DEPS_ACTIVOS = 'http://www.parlamento.pt/DeputadoGP/Paginas/Deputadoslista.aspx'
FORMATTER_URL_BIO_DEP = 'http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%d'

RE_NAME = re.compile('Nome.*Text')
RE_SHORT = re.compile('NomeDeputado')
RE_BIRTHDATE = re.compile('DOB.*Text')
RE_PARTY = re.compile('Partido')
RE_OCCUPATION = re.compile('Prof')
RE_EDUCATION = re.compile('Habilitacoes')
RE_CURRENT_JOBS = re.compile('CargosDesempenha')
RE_JOBS = re.compile('CargosExercidos')
RE_AWARDS = re.compile('Condecoracoes')
RE_COMS = re.compile('Comissoes')
RE_MANDATES = re.compile('TabLegs')


def hash(str):
    hash = sha1()
    hash.update(str)
    return hash.hexdigest()


def file_get_contents(file):
    return open(file).read()


def file_put_contents(file, contents):
    codecs.open(file, 'w+', 'utf-8').write(contents)


def getpage(url):
    if not os.path.exists('cache'):
        log.info('Creating new cache/ folder.')
        os.mkdir('cache')
    url_hash = hash(url)
    cache_file = 'cache/' + url_hash

    if os.path.exists(cache_file):
        log.debug("Cache hit for %s" % url)
        page = file_get_contents(cache_file)
    else:
        log.debug("Cache miss for %s" % url)
        page = urllib.urlopen(url).read()
        file_put_contents(cache_file, page)
    return page


def parse_legislature(s):
    s = s.replace('&nbsp;', '')
    number, dates = s.split('[')
    number = ROMAN_NUMERALS[number.strip()]
    dates = dates.strip(' ]')
    if len(dates.split(' a ')) == 2:
        start, end = dates.split(' a ')
    else:
        start = dates.split(' a ')[0]
        end = ''
    if start.endswith(' a'):
        start = start.replace(' a', '')
    return number, start, end


def get_active_deps():
    # returns list of BIDs
    ids = []
    try:
        log.info("Fetching active MP list...")
        deps_activos_list = getpage(URL_DEPS_ACTIVOS)
        soup = BeautifulSoup(deps_activos_list, "lxml")
    except:  # há muitos erros http ou parse que podem ocorrer
        soup = None
        log.warning('Active MP page could not be fetched.')
        raise

    table_deps = soup.find('table', 'ARTabResultados')
    deps = table_deps.findAll('tr', 'ARTabResultadosLinhaPar')
    deps += table_deps.findAll('tr', 'ARTabResultadosLinhaImpar')
    for dep in deps:
        depurl = dep.td.a['href']
        dep_bid = int(depurl[depurl.find('BID=') + 4:])
        ids.append(dep_bid)

    log.info('Active MP list created.')
    return ids


def extract_details(block):
    return [item.text.strip() for item in block.find_all('tr')[1:]]


def extract_multiline_details(block):
    return [item.strip(" ;,") for item in chain.from_iterable(tr.text.split('\n') for tr in block.find_all('tr')[1:]) if item]


def process_dep(i):
    log.debug("Trying ID %d..." % i)

    url = FORMATTER_URL_BIO_DEP % i
    soup = BeautifulSoup(getpage(url), "lxml")
    name = soup.find('span', id=RE_NAME)
    if name:
        short = soup.find('span', id=RE_SHORT)
        birthdate = soup.find('span', id=RE_BIRTHDATE)
        party = soup.find('span', id=RE_PARTY)
        occupation = soup.find('div', id=RE_OCCUPATION)
        education = soup.find('div', id=RE_EDUCATION)
        current_jobs = soup.find('div', id=RE_CURRENT_JOBS)  # ;)
        jobs = soup.find('div', id=RE_JOBS)  # ;)
        awards = soup.find('div', id=RE_AWARDS)
        coms = soup.find('div', id=RE_COMS)
        mandates = soup.find('table', id=RE_MANDATES)

        deprow = {'id': i,
                  'name': name.text,
                  'url': url,
                  'scrape_date': dt.utcnow().isoformat()}

        if short:
            # replace by canonical shortnames if appropriate
            if short.text in SHORTNAME_REPLACES:
                t = SHORTNAME_REPLACES[short.text]
            else:
                t = short.text
            deprow['shortname'] = t
        if birthdate:
            deprow['birthdate'] = birthdate.text
        if party:
            deprow['party'] = party.text
        if education:
            # TODO: break educations string into multiple entries, ';' is the separator
            deprow['education'] = extract_details(education)
        if occupation:
            deprow['occupation'] = extract_details(occupation)
        if jobs:
            deprow['jobs'] = extract_multiline_details(jobs)
        if current_jobs:
            deprow['current_jobs'] = extract_multiline_details(current_jobs)
        if coms:
            deprow['commissions'] = extract_details(coms)
        if awards:
            deprow['awards'] = extract_multiline_details(awards)
        if mandates:
            # TODO: this block may take advantage of the new functions
            deprow['mandates'] = []
            for each in mandates.findAll('tr')[1:]:
                leg = each.findAll('td')
                l = leg[0].text
                number, start, end = parse_legislature(l)
                end = end.rstrip(']\n')

                mandate = {
                    'legislature': number,
                    'start_date': start,
                    'end_date': end,
                    'constituency': leg[3].text,
                    'party': leg[4].text
                }

                if leg[1].find("a"):
                    # atividade parlamentar
                    url = leg[1].find("a")['href']
                    if not url.startswith("http://"):
                        url = "http://www.parlamento.pt" + url
                    mandate['activity_url'] = url
                if leg[2].find("a"):
                    # registo de interesses
                    url = leg[2].find("a")['href']
                    if not url.startswith("http://"):
                        url = "http://www.parlamento.pt" + url
                    mandate['interest_url'] = url
                deprow['mandates'].append(mandate)

        log.info("Scraped MP: %s" % short.text)

        return deprow


def scrape(format, start=1, end=None, verbose=False, outfile='', indent=1, processes=2):
    pool = multiprocessing.Pool(processes=processes)
    max = end
    deprows = {}
    active_ids = get_active_deps()

    try:
        processed_deps = (proced_dep for proced_dep in pool.map(process_dep, range(start, max), chunksize=4) if proced_dep)
    except KeyboardInterrupt:
        pool.terminate()

    for processed_dep in processed_deps:
        deprows[processed_dep['id']] = processed_dep

    for k in deprows.keys():
        if deprows[k]['id'] in active_ids:
            deprows[k]['active'] = True
        else:
            deprows[k]['active'] = False

    log.info("Saving to file %s..." % outfile)
    if format == "json":
        depsfp = codecs.open(outfile, 'w+', 'utf-8')
        depsfp.write(dumps(deprows, encoding='utf-8', ensure_ascii=False, indent=indent, sort_keys=True))
        depsfp.close()
    elif format == "csv":
        depsfp = open(outfile, 'w+')
        writer = csv.DictWriter(depsfp, delimiter=",", quoting=csv.QUOTE_NONNUMERIC, quotechar='"', fieldnames=fieldnames)
        writer.writeheader()
        for rownumber in deprows:
            row = deprows[rownumber]
            row.pop("mandates")
            for key in row:
                if type(row[key]) == list:
                    # convert lists to ;-separated strings
                    row[key] = "; ".join(row[key])
            row = {k: v.strip().encode('utf-8') if type(v) in (str, unicode) else v for k, v in row.items()}
            writer.writerow(row)
    log.info("Done.")


@click.command()
@click.option("-f", "--format", help="Output file format, can be json (default) or csv", default="json")
@click.option("-s", "--start", type=int, help="Begin scrape from this ID (int required, default 0)", default=0)
@click.option("-e", "--end", type=int, help="End scrape at this ID (int required, default 5000)", default=5000)
@click.option("-v", "--verbose", is_flag=True, help="Print some helpful information when running")
@click.option("-o", "--outfile", type=click.Path(), help="Output file (default is deputados.json)")
@click.option("-i", "--indent", type=int, help="Spaces for JSON indentation (default is 2)", default=2)
@click.option("-p", "--processes", type=int, help="Simultaneous processes to run (default is 2)", default=2)
@click.option("-c", "--clear-cache", help="Clean the local webpage cache", is_flag=True)
def main(format, start, end, verbose, outfile, indent, clear_cache, processes):
    if not outfile and format == "csv":
        outfile = "deputados.csv"
    elif not outfile and format == "json":
        outfile = "deputados.json"
    if clear_cache:
        log.info("Clearing old cache...")
        shutil.rmtree("cache/")

    scrape(format, start, end, verbose, outfile, indent, processes)

if __name__ == "__main__":
    main()
