import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys,time,hashlib,os
sys.path.append('../utils')
from database import insertRecord, dbQuery

# Load environment variables from .env file
load_dotenv()

# a mechanism to skip records which were already loaded, delete from db to undo, or set to False
hv_resume=os.environ.get("HV_RESUME") or True
hv_done = dbQuery("select identifier, hash from harvest.items where source='ESDAC'")
def hv_next(id):
    if hv_resume:
        for rec in sorted(hv_done):
            rid,hsh = rec
            if id==rid.split('#')[0]:
                return False
    return True

def fullurl(u):
    if u.startswith('/'):
        u = 'https://esdac.jrc.ec.europa.eu/'+u
    return u

startTime = time.perf_counter()
def elapsed():
    return f"{(time.perf_counter() - startTime):0.1f}s"

print('Fetch ESDAC datasets')
for i in range(0,4):
    url = f'https://esdac.jrc.ec.europa.eu/resource-type/datasets?page={i}'
    print(f'{elapsed()} Page {url}')
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    for tr in soup.find_all("div", {"class": "views-row"}):
        for a in tr.find_all('a'):
            uri = fullurl(a.get('href'))
            if hv_next(uri):
                print(f"{elapsed()} Fetch Subpage: {uri}")
                html = requests.get(uri).text
                print(f'{elapsed()} Page loaded')
                section = ""
                s2 = BeautifulSoup(html, 'html.parser')
                for t in s2.find_all("title"):
                    ttl = t.text
                for s3 in s2.find_all("section",{'id':'block-system-main'}):
                    section = str(s3)
                hashcode = hashlib.md5(section.encode("utf-8")).hexdigest() # get unique hash for html 
                insertRecord(   identifier=uri,
                        uri=uri,
                        identifiertype='uri',
                        title=ttl,
                        resulttype='HTML',
                        resultobject=str(section),
                        hashcode=hashcode,
                        source='ESDAC',
                        itemtype='dataset') # insert into db
            break # only first link (title)
            
print('Fetch EUDASM maps')
for i in range(0,218):
    j=0
    url = f'https://esdac.jrc.ec.europa.eu/resource-type/national-soil-maps-eudasm?page={i}'
    if hv_next(url):
        print(f'{elapsed()} Page {url}')
        html = requests.get(url).text
        print(f'{elapsed()} Page loaded')
        soup = BeautifulSoup(html, 'html.parser')
        for tr in soup.find_all("div", {"class": "views-row"}):
            j=j+1
            hashcode = hashlib.md5(tr.encode("utf-8")).hexdigest() # get unique hash for html 
            insertRecord(   identifier=f'{url}#{i}-{j}',
                            uri='',
                            identifiertype='uri',
                            resulttype='HTML',
                            resultobject=str(tr),
                            hashcode=hashcode,
                            source='ESDAC',
                            itemtype='dataset') # insert into db
    
print('Fetch ESDAC documents')
for i in range(0,21):
    url = f'https://esdac.jrc.ec.europa.eu/resource-type/documents?page={i}'
    if hv_next(uri):
        print(f'{elapsed()} Page {url}')
        html = requests.get(url).text
        print(f'{elapsed()} Page loaded')
        soup = BeautifulSoup(html, 'html.parser')
        j=0
        for tr in soup.find_all("div", {"class": "views-row"}):
            j=j+1
            hashcode = hashlib.md5(tr.encode("utf-8")).hexdigest() # get unique hash for html 
            insertRecord(   identifier=f'{url}#{i}-{j}',
                            uri='',
                            identifiertype='uri',
                            resulttype='HTML',
                            resultobject=str(tr),
                            hashcode=hashcode,
                            source='ESDAC',
                            itemtype='document') # insert into db