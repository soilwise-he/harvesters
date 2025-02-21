from dotenv import load_dotenv
from datetime import datetime
from time import mktime
import feedparser, os, sys, json
sys.path.append('utils')
from database import dbInit, dbQuery
load_dotenv()

sql = """CREATE TABLE IF NOT EXISTS harvest.feeds (
            published TIMESTAMP,
            title TEXT,
            summary TEXT,
            link TEXT PRIMARY KEY,
            image TEXT,
            author TEXT,
            tags TEXT,
            asjson TEXT,
            imported TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
        )"""
dbQuery(sql,None,False)

# Load environment variables from .env file


conn = dbInit()
cursor = conn.cursor()

# print('truncate records')
# cursor.execute("truncate table harvest.feeds")   

for fd in os.environ.get("FEED_URLS").split(','):
    fdp = feedparser.parse(fd)
    print('Feed:',fd)
    if fdp.bozo_exception:
        print (fdp.bozo_exception)
    else:
        for ent in fdp.entries:
            print('-',ent.get('title',''))
            if ent.get('link') not in [None,'']:
                cursor.execute('insert into harvest.feeds (published,title,summary,link,image,author,tags,asjson) values (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',
                    (datetime.fromtimestamp(mktime(ent.get('published_parsed',''))), ent.get('title',''), ent.get('summary',''), ent.get('link',''), 
                    ent.get('image',{}).get('href',''), ent.get('author',''), ';'.join([t.get('term','') for t in ent.get('tags',[])]), json.dumps(ent) )
                )

conn.commit() 


