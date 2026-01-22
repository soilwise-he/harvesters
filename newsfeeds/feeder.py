from dotenv import load_dotenv
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from time import mktime
import feedparser, os, sys, json
sys.path.append('utils')
from database import dbInit, dbQuery
# Load environment variables from .env file
load_dotenv()

headers = {"User-Agent": "Soilwise Harvest v0.2"}

sql = """CREATE TABLE IF NOT EXISTS harvest.feeds (
            published TIMESTAMP,
            title TEXT,
            summary TEXT,
            link TEXT PRIMARY KEY,
            image TEXT,
            author TEXT,
            tags TEXT,
            asjson TEXT,
            project TEXT,
            imported TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
        )"""
dbQuery(sql,None,False)

### Sample <link rel="alternate" type="application/rss+xml" title="hort2thefuture.eu &raquo; Feed" href="https://hort2thefuture.eu/feed/" />

sql = "SELECT code, website from harvest.projects where website is not null"
recs = dbQuery(sql,None,True)
conn = dbInit()
cursor = conn.cursor()
for row in recs:
    p,u = row
    if u.startswith('http'):
        try:
            html = requests.get(u,headers=headers).text
            soup = BeautifulSoup(html, "html.parser")
            fd = None
            for l in soup.find_all("link", {"rel": "alternate"}):
                if l.get('type') == "application/rss+xml":
                    fd0 = l.get('href')
                    if fd0 and fd0.startswith('http'):
                        fd=fd0
                        break
                # elif l.attr('type') == "text/calendar": # calendar events
            if fd not in [None,'']:
                fdp = feedparser.parse(fd)
                print('Project:',p,'Feed:',fd)
                if 'bozo_exception' in fdp:
                    print (fdp.get('bozo_exception',''))
                else:
                    for ent in fdp.entries:
                        print('-',ent.get('title',''))
                        if ent.get('link') not in [None,'']:
                            cursor.execute('insert into harvest.feeds (published,title,summary,link,image,author,tags,asjson,project) values (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',
                                (datetime.fromtimestamp(mktime(ent.get('published_parsed',''))), ent.get('title',''), ent.get('summary',''), ent.get('link',''), 
                                ent.get('image',{}).get('href',''), ent.get('author',''), ';'.join([t.get('term','') for t in ent.get('tags',[])]), json.dumps(ent), p )
                            )
        except Exception as e:
            print(f'Failed getting {u}, {e}')

conn.commit() 


