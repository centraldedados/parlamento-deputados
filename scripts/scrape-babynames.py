#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pedro Rodrigues - medecau.com - medecau@gmail.com
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from csv import writer
from urllib import urlopen

'''
More info:
http://www.pinkblue.com/nomes/desc.asp?id=449
http://babynamesworld.parentsconnect.com/profile.php?name=Pedro
http://www.babynames.com/Names/search.php?searchby=byname&searchterm=Pedro
'''

def get_page(url):
    return urlopen(urlopen).read()

base_path='http://ferrao.org/onomastica/'
csv_writer=writer(open('nome_genero.csv', 'w'))

print 'Reading initial page...'
page=get_page(base_path)

soup = BeautifulSoup(page)

alphabet_div=soup.body.form.div.table.contents[1].td.div

alphabet_pages={}

print 'Generating list of pages to visit...'
for each_page in alphabet_div:
    try:
        alphabet_pages[each_page.a.string]=each_page.a['href']
    except:
        pass

print 'Iterating over pages...'
for letter, page in alphabet_pages.iteritems():
    print 'Page %s for %s' % (page, letter)
    page=get_page(base_path+page)
    soup = BeautifulSoup(page)
    names_tr=soup.html.body.form.contents[6].tr
    for each_td in names_tr:
        for each in each_td:
            new_row=[]
            try:
                if each.name=='a':
                    new_row.append(BeautifulStoneSoup(each.string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES))
                    if each['style'].find('#ff6790')>-1:
                        new_row.append('F')
                    elif each['style'].find('#0097ff')>-1:
                        new_row.append('M')
                    else:
                        new_row.append('')
                    
                    csv_writer.writerow(new_row)
            except:
                pass
