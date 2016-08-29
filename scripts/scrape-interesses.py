#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""

# http://www.parlamento.pt/DeputadoGP/Paginas/RegistoInteresses.aspx?BID=3

- extende informações de cada deputado
- ver: depscrap.py

"""

from BeautifulSoup import BeautifulSoup
from json import dumps
from json import loads
from utils import *

FORMATTER_URL_INTERESSES='http://www.parlamento.pt/DeputadoGP/Paginas/RegistoInteresses.aspx?BID=%d'

deps = loads(file_get_contents('o.json'))
print dumps(deps, indent=2)

for e in deps.iterkeys():
    url=FORMATTER_URL_INTERESSES % deps[e]['id']
    soup = BeautifulSoup(getpage(url))
    
    civil = soup.find('span',dict(id='ctl00_ctl13_g_d22c802e_0a80_4ab1_b44e_335a72b3cc14_ctl00_lblEstadoCivil'))
    partner_name = soup.find('span',dict(id='ctl00_ctl13_g_d22c802e_0a80_4ab1_b44e_335a72b3cc14_ctl00_lblNomeConjuge'))
    type_partnership = soup.find('span',dict(id='ctl00_ctl13_g_d22c802e_0a80_4ab1_b44e_335a72b3cc14_ctl00_lblRegimeBens'))
    
    if civil:
        deps[e]['marital_status']=civil.text
    if partner_name:
        deps[e]['partner_name']=partner_name.text
    if type_partnership:
        deps[e]['partnership_type']=type_partnership.text

file_put_contents('o.json', dumps(deps, encoding='utf-8', indent=1, sort_keys=True))

