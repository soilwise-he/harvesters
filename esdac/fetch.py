import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys,time,hashlib,os
sys.path.append('utils')
from database import insertRecord, dbQuery

# Load environment variables from .env file
load_dotenv()

def fullurl(u):
    if not u.startswith('http'):
        if u.startswith('/'):
            u = 'https://esdac.jrc.ec.europa.eu'+u
        else:    
            u = 'https://esdac.jrc.ec.europa.eu/'+u
    return u

startTime = time.perf_counter()
def elapsed():
    return f"{(time.perf_counter() - startTime):0.1f}s"

# for debug, select types to harvest
types = ['dataset','maps','document']
headers = {'Accept': 'text/html', "User-Agent": "Soilwise Harvest v0.1"}

if 'dataset' in types:
    print('Fetch ESDAC datasets')
    duplicates = []
    for i in range(0,5):
        url = f'https://esdac.jrc.ec.europa.eu/resource-type/datasets?page={i}'
        print(f'{elapsed()} Page {url}')
        html = requests.get(url,headers=headers).text
        soup = BeautifulSoup(html, "html.parser")
        for tr in soup.find_all("div", {"class": "views-row"}):
            uri = fullurl(tr.find('a').get('href'))
            if uri not in duplicates:
                duplicates.append(uri)
                print(f"{elapsed()} Fetch Subpage: {uri}")
                html = requests.get(uri,headers=headers).text
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

if 'map' in types:
    print('Fetch EUDASM maps')
    duplicates = []
    for i in range(0,218):
        url = f'https://esdac.jrc.ec.europa.eu/resource-type/national-soil-maps-eudasm?page={i}'
        print(f'{elapsed()} Page {url}')
        html = requests.get(url,headers=headers).text
        print(f'{elapsed()} Page loaded')
        soup = BeautifulSoup(html, 'html.parser')
        for tr in soup.find_all("div", {"class": "views-row"}):
            f = tr.find("a",{"title":"File"})
            if f:
                doc_uri = fullurl(f.get('href')) #set the id to ds url
                if doc_uri not in duplicates:
                    duplicates.append(doc_uri)
                    print(f'insert {doc_uri}')
                    hashcode = hashlib.md5(tr.encode("utf-8")).hexdigest() # get unique hash for html 
                    insertRecord(   identifier=f'{doc_uri}',
                                    uri='{doc_uri}',
                                    identifiertype='uri',
                                    resulttype='HTML',
                                    resultobject=str(tr),
                                    hashcode=hashcode,
                                    source='ESDAC',
                                    itemtype='dataset') # insert into db
                else:
                    print(f'duplicate {doc_uri}')
            else:
                print('no url')
    
if 'document' in types:
    print('Fetch ESDAC documents')
    duplicates = []
    for i in range(0,25):
        url = f'https://esdac.jrc.ec.europa.eu/resource-type/documents?page={i}'
        print(f'{elapsed()} Page {url}')
        html = requests.get(url,headers=headers).text
        print(f'{elapsed()} Page loaded')
        soup = BeautifulSoup(html, 'html.parser')
        for tr in soup.find_all("div", {"class": "views-row"}):
            doc_uri = None
            # find a uri (filename)
            for f in tr.find_all("a",{"aria-label":"Download"}):
                doc_uri = f.get('href')
            if not doc_uri:
                for f in tr.find_all("span",{"class":"file"}):
                    for fl in f.find_all("a"):
                        doc_uri = fl.get('href')
                        break

            if doc_uri not in [None,''] and doc_uri not in duplicates:
                if 'doi.org' in doc_uri:
                    doc_uri2 = doc_uri.split('doi.org/').pop()
                    tp='doi'
                else:
                    doc_uri2 = fullurl(doc_uri)
                    tp = 'uri'
                duplicates.append(doc_uri)
                print(f'insert {doc_uri}')
                hashcode = hashlib.md5(tr.encode("utf-8")).hexdigest() # get unique hash for html 
                insertRecord(   identifier=doc_uri2,
                                uri=doc_uri2,
                                identifiertype=tp,
                                resulttype='HTML',
                                resultobject=str(tr),
                                hashcode=hashcode,
                                source='ESDAC',
                                itemtype='document') # insert into db
            else:
                print('no url')