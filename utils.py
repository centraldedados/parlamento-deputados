from hashlib import sha1
import os
import urllib

#USE: from utils import *

def hash(str):
    hash = sha1()
    hash.update(str)
    return hash.hexdigest()

def file_get_contents(file):
    return open(file).read()
def file_put_contents(file, contents):
    open(file, 'w+').write(contents)

def getpage(url):
    if not os.path.exists('cache'):
        print 'Creating new cache/ folder.'
        os.mkdir('cache')
    url_hash = hash(url)
    cache_file = 'cache/' + url_hash
    
    if os.path.exists(cache_file):
        page = file_get_contents(cache_file)
    else:
        page = urllib.urlopen(url).read()
        file_put_contents(cache_file, page)
    return page
