#!/usr/bin/python
"""
Extrai imagens de cada deputado
"""
import os
from urllib import urlretrieve
import json
from zenlog import log

mp_file = 'deputados.json'
pic_url_formatter = 'http://app.parlamento.pt/webutils/getimage.aspx?id=%s&type=deputado'
dest = 'imgs/'


def main():
    if not os.path.exists(dest):
        os.mkdir(dest)
        log.info("Directory 'imgs/' created.")

    mp_json = json.loads(open(mp_file, 'r').read())
    for mp_id in mp_json:
        url = pic_url_formatter % mp_id
        filename = '%s.jpg' % os.path.join(dest, mp_id)
        if os.path.exists(filename):
            log.debug("File for id %s already exists, skipping." % mp_id)
            continue
        log.info('Retrieving picture with id: %s' % mp_id)
        try:
            urlretrieve(url, filename)
        except IOError:
            log.error('Socket error! :(')

    log.info('Done. Now do find ./imgs/ -size -722c -exec rm {} \;')
    log.info('to clean up things.')

if __name__ == '__main__':
    main()
