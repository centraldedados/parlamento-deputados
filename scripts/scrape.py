#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import re
from itertools import chain
from json import dumps
import io
import csv
import logging
import multiprocessing
import click
from bs4 import BeautifulSoup
from name_replaces import SHORTNAME_REPLACES
from utils import getpage, slugify

logger = logging.getLogger(__name__)

FIELDNAMES = ['id', 'shortname', 'name', 'party', 'active', 'education', 'birthdate', 'occupation', 'current_jobs',
              'jobs', 'commissions', 'mandates', 'awards', 'url_democratica', 'url_parlamento', 'image_url']

DEFAULT_MAX = 5700

ROMAN_NUMERALS = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
                  'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
                  'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
                  'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
                  'XXI': 21, 'XXII': 22, 'XXIII': 23, 'XXIV': 24, 'XXV': 25}

ACTIVE_MP_URL = 'http://www.parlamento.pt/DeputadoGP/Paginas/Deputados.aspx'
MP_BIO_URL_FORMATTER = 'http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%d'

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


def get_active_mps():
    # returns list of BIDs
    ids = []
    try:
        logger.info("Fetching active MP list...")
        active_mp_list = getpage(ACTIVE_MP_URL)
        soup = BeautifulSoup(active_mp_list, "lxml")
    except:  # há muitos erros http ou parse que podem ocorrer
        logger.warning('Active MP page could not be fetched.')
        raise

    table_mps = soup.find('table', 'ARTabResultados')
    mps = table_mps.findAll('tr', 'ARTabResultadosLinhaPar')
    mps += table_mps.findAll('tr', 'ARTabResultadosLinhaImpar')
    for mp in mps:
        mpurl = mp.td.a['href']
        mp_bid = int(mpurl[mpurl.find('BID=') + 4:])
        ids.append(mp_bid)

    logger.info('Active MP list created.')
    return ids


def extract_details(block):
    return [item.text.strip() for item in block.find_all('tr')[1:]]


def extract_multiline_details(block):
    return [item.strip(" ;,") for item in chain.from_iterable(tr.text.split('\n') for tr in block.find_all('tr')[1:]) if item]


def process_mp(i):
    logger.debug("Trying ID %d..." % i)

    url = MP_BIO_URL_FORMATTER % i
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
        image_src = soup.find('td', {'class': 'tdFotoBio'}).img['src']

        mprow = {'id': i,
                 'name': name.text,
                 'url_parlamento': url}

        if short:
            # replace by canonical shortnames if appropriate
            if short.text in SHORTNAME_REPLACES:
                t = SHORTNAME_REPLACES[short.text]
            else:
                t = short.text
            mprow['shortname'] = t
            mprow['url_democratica'] = 'http://demo.cratica.org/deputados/%s/' % slugify(t)
        if birthdate:
            mprow['birthdate'] = birthdate.text
        if party:
            mprow['party'] = party.text
        if education:
            # TODO: break educations string into multiple entries, ';' is the separator
            mprow['education'] = extract_details(education)
        if occupation:
            mprow['occupation'] = extract_details(occupation)
        if jobs:
            mprow['jobs'] = extract_multiline_details(jobs)
        if current_jobs:
            mprow['current_jobs'] = extract_multiline_details(current_jobs)
        if coms:
            mprow['commissions'] = extract_details(coms)
        if awards:
            mprow['awards'] = extract_multiline_details(awards)
        if mandates:
            # TODO: this block may take advantage of the new functions
            mprow['mandates'] = []
            for each in mandates.findAll('tr')[1:]:
                leg = each.findAll('td')
                l = leg[0].text
                number, start, end = parse_legislature(l)
                end = end.rstrip(']\n')

                mandate = {
                    'legislature': number,
                    'start_date': start,
                    'end_date': end,
                    'constituency': leg[4].text,
                    'party': leg[5].text
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
                mprow['mandates'].append(mandate)
        if image_src:
            mprow['image_url'] = image_src

        logger.info("Scraped MP: %s" % short.text)

        return mprow


def scrape(format, start=1, end=None, outfile='', indent=1, processes=2):
    # Start with including the old MP list (those not on Parlamento.pt)
    # TODO
    # from utils import getpage, load_csv
    # csvkeys = ('leg', 'constituency_code', 'constituency', 'party', 'name', 'date_start', 'date_end')
    # data = load_csv('deputados-antigos.csv', keys=csvkeys, header=True)
    # return data

    pool = multiprocessing.Pool(processes=processes)
    max = end
    mprows = {}
    active_ids = get_active_mps()

    try:
        processed_mps = (processed_mp for processed_mp in pool.map(process_mp, range(start, max), chunksize=4) if processed_mp)
    except KeyboardInterrupt:
        pool.terminate()

    for processed_mp in processed_mps:
        mprows[processed_mp['id']] = processed_mp

    for k in mprows.keys():
        if mprows[k]['id'] in active_ids:
            mprows[k]['active'] = True
        else:
            mprows[k]['active'] = False

    logger.info("Saving to file %s..." % outfile)
    if format == "json":
        depsfp = io.open(outfile, 'w+')
        depsfp.write(dumps(mprows, encoding='utf-8', ensure_ascii=False, indent=indent, sort_keys=True))
        depsfp.close()
    elif format == "csv":
        depsfp = open(outfile, 'w+')
        writer = csv.DictWriter(depsfp, delimiter=",", quoting=csv.QUOTE_NONNUMERIC, quotechar='"', fieldnames=FIELDNAMES)
        writer.writeheader()
        for rownumber in mprows:
            row = mprows[rownumber]
            row.pop("mandates")
            for key in row:
                if type(row[key]) == list:
                    # convert lists to ;-separated strings
                    row[key] = "; ".join(row[key])
            row = {k: v.strip().encode('utf-8') if type(v) in (str, unicode) else v for k, v in row.items()}
            writer.writerow(row)
    logger.info("Done.")


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
    if verbose:
        import sys
        root = logging.getLogger()
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        root.setLevel(logging.INFO)
        root.addHandler(ch)
    if not outfile and format == "csv":
        outfile = "deputados.csv"
    elif not outfile and format == "json":
        outfile = "deputados.json"
    if clear_cache:
        logger.info("Clearing old cache...")
        shutil.rmtree("cache/")

    scrape(format, start, end, outfile, indent, processes)

if __name__ == "__main__":
    main()
