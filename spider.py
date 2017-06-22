#Crawls a website and gathers href=urls and using many to many tables in SQL
#to show refrenced pages and where their links occur
#Can be run/rerun until site is interpreted
#

#Will be the basis for SCRAPER with functionality
#Readability score
#find 'broken' pages (404)
#getimagelinks
#getdocumentlinks
#Python 3.x


#set root dir
import os
import sys
os.chdir(sys.path[0])
print(sys.path[0])

import sqlite3
import urllib.request
import urllib.parse
import urllib.error
import ssl
import re
#BeautifulSoup stuff bs4 in Py3
from bs4 import *

countquit = 0

conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Pages
    (id INTEGER PRIMARY KEY, url TEXT UNIQUE, html TEXT,
     error INTEGER)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Links
    (from_id INTEGER, to_id INTEGER)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Webs (url TEXT UNIQUE)''')

# Check to see if we are already in progress...
cur.execute('SELECT id,url FROM Pages WHERE html is NULL and error is NULL ORDER BY RANDOM() LIMIT 1')
row = cur.fetchone()
if row is not None:
    print ("Restarting existing crawl.  Remove spider.sqlite to start a fresh crawl.")
else :
    starturl = input('Enter web url or enter: ')
    if ( len(starturl) < 1 ) : starturl = 'https://www.locknar.com'
    if ( starturl.endswith('/') ) : starturl = starturl[:-1]
    web = starturl

    if ( starturl.endswith('.htm') or starturl.endswith('.html') ) :
        pos = starturl.rfind('/')
        web = starturl[:pos]

    if ( len(web) > 1 ) :
        cur.execute('INSERT OR IGNORE INTO Webs (url) VALUES ( ? )', ( web, ) )
        cur.execute('INSERT OR IGNORE INTO Pages (url, html) VALUES ( ?, NULL)', ( starturl, ) )
        conn.commit()

# Get the current webs
cur.execute('''SELECT url FROM Webs''')
webs = list()
for row in cur:
    webs.append(str(row[0]))

print (webs)

counter = 0
while True:
    if ( counter < 1 ) :
        sval = input('How many pages:')
        if ( len(sval) < 1 ) : break
        counter = int(sval)
    counter -= 1

    cur.execute('SELECT id,url FROM Pages WHERE html is NULL and error is NULL ORDER BY RANDOM() LIMIT 1')

    try:
        row = cur.fetchone()
        fromid = row[0]
        url = row[1]
    except:
        print ('No unretrieved HTML pages found')
        many = 0
        break
    try:
        document = urllib.request.urlopen(url)

    except KeyboardInterrupt:
        print ('')
        print ('Program interrupted by user...')
        break
    except:
        print ("Error on page: ", url)
        cur.execute('UPDATE Pages SET error=? WHERE url=?', (-1, url) )
        conn.commit()
        continue


    print (fromid, url)

    if ( url.endswith('.png') or url.endswith('.jpg') or url.endswith('.gif') ) or url.endswith('.pdf') or url.endswith('.doc'):
        html = 'No html'
    else:
        html = document.read()
    try:
        soup = BeautifulSoup(html, 'html.parser')
        countquit=0
    except:
        continue
        countquit += 1
        if countquit > 5:
            break
    cur.execute('INSERT OR IGNORE INTO Pages (url, html) VALUES ( ?, NULL)', ( url,   ) )
    cur.execute('UPDATE Pages SET html=? WHERE url=?', (html, url ) )
    conn.commit()

        # Retrieve all of the anchor tags
    tags = soup()
    for tag in tags:
        href = tag.get('href', None)
        if ( href is None ) : continue
        #Check whats read
        #print(href)
        # Check if the URL is in any of the webs
        found = False
        for web in webs:
            if ( href.startswith(web) ) :
                found = True
                break
        if not found : continue

        cur.execute('INSERT OR IGNORE INTO Pages (url, html) VALUES ( ?, NULL)', ( href, ) )

        cur.execute('SELECT id FROM Pages WHERE url=? LIMIT 1', ( href, ))
        try:
            row = cur.fetchone()
            toid = row[0]
        except:
            print ('Could not retrieve id')
            continue
        # print fromid, toid
        cur.execute('INSERT OR IGNORE INTO Links (from_id, to_id) VALUES ( ?, ? )', ( fromid, toid ) )



    conn.commit()
cur.close()
