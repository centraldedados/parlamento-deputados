#!/usr/bin/python
"""

- extrai imagens de cada deputado
- ver: depscrap.py

"""
import sys, os
from urllib import urlretrieve
import json

mp_file = '/home/rlafuente/proj/thd/datasets/deputados.json'
pic_url_formatter='http://app.parlamento.pt/webutils/getimage.aspx?id=%s&type=deputado'
dest='imgs/'

def main():
    if not os.path.exists(dest):
        os.mkdir(dest)
        print "Directory 'imgs/' created."

    # csv_MP=reader(open('MP.csv'),delimiter='|', quotechar='"')
    mp_json = json.loads(open(mp_file, 'r').read())
    for mp_id in mp_json:
        # only for new ones, remove later
        if int(mp_id) > 4200:
            continue
        print 'retrieving picture with id: %s' % mp_id
        try:
            urlretrieve(pic_url_formatter % mp_id, '%s%s.jpg' % (dest,mp_id))
        except IOError:
            print '- Socket error! :('
    
    print "it's almost done"
    print 'do find ./imgs/ -size -722c -exec rm {} \;'
    print 'to clean up things'

if __name__ == '__main__':
    main()






