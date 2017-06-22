#Status: Works: Returns Error Links and Pages where errors occur
#Python 3.x

#set root dir
import os
import sys
os.chdir(sys.path[0])
print(sys.path[0])

import sqlite3

conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

#Auritas bad link lookup get ids of from location [1]
cur.execute('''SELECT id, from_id FROM Links JOIN Pages ON id=to_id WHERE error = -1 ORDER BY id DESC''')
fromids=cur.fetchall()

count=0
priorid=0
curid=0
for row in fromids:
    curid=row[0]
    #id of bad link
    cur.execute('''SELECT url FROM Pages WHERE id = ?''', ( row[0], ))
    badurl=cur.fetchone()
    #id of pages with bad link
    cur.execute('''SELECT url FROM Pages WHERE id = ?''', ( row[1], ))
    badref=cur.fetchone()
    if priorid==curid:
        print('    ',badref[0])
    else:
        print('Bad Link: ', badurl[0])
        print('    Is referenced on:')
        print('    ',badref[0])
        priorid=curid
    count+=1
if count is 0:
    print('Scrape Had no Broken links.')
print(count)


cur.close()
