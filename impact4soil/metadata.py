import requests

from dotenv import load_dotenv
import sys,time,hashlib,os
sys.path.append('utils')
from database import insertRecord, dbQuery, hasSource
# Load environment variables from .env file
load_dotenv()

def stripdoi(uri):
    if 'doi.org/' in uri:
        return uri.split('doi.org/').pop()
    elif 'geonetwork/' in uri:
        return uri.split('/').pop()
    else:
        return uri

def tp(id):
    if 'doi.org' in id:
        return 'doi'
    elif 'geonetwork' in id:
        return 'uuid'
    elif id.startswith('http'):
        return 'uri'
    else:
        return 'uuid'


label = "IMPACT4SOIL"


if os.environ.get("HARVESTTYPES"):
    harvesttypes = os.environ.get("HARVESTTYPES").split(',')
else:
    harvesttypes = ['document','dataset']

# harvest   publications
if 'document' in harvesttypes:
    url="https://www.impact4soil.com/scientific-evidence/publicationstojson"
    # add source if it does not exist
    hasSource(label,url,'',label)
    
    count=20
    page=1
    max=10000
    print('Impact4Soil Publications')
    while count > 0 and (page*20 < max):
        headers = {'Accept': 'application/json', "User-Agent": "Soilwise Harvest v0.1"}
        proceed = True
        records = []
        try:
            resp = requests.get(f"{url}?page={page}",headers=headers)
            records = resp.json()
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            proceed = False
            print(f'Error fetching {url}?page={page}, {e}')
        
        if proceed : 
            cnt = 1
            count=len(records)
            for r in records: 
                print(f"{(page-1)*20+cnt}. {r.get('url',r.get('id'))}")
                cnt=cnt+1
                id = r.get('url',r.get('id'))
                if r.get('url','').startswith('http'):
                    hashcode = hashlib.md5(str(r).encode("utf-8")).hexdigest() # get unique hash for html 
                    insertRecord(   identifier=stripdoi(id),
                                    uri=r.get('url'),
                                    identifiertype=tp(id),
                                    title=r.get('title',''),
                                    resulttype='JSON',
                                    resultobject=str(r),
                                    hashcode=hashcode,
                                    source=label,
                                    itemtype='document') # insert into db
        page = page+1

# harvest datasets
if 'dataset' in harvesttypes:
    url = "https://www.impact4soil.com/datasets-api/datasets" # ?size=5&page=10
    # add source if it does not exist
    hasSource(label,url,'',label)
    count=10
    page=1
    size=50
    max=50
    print('Impact4Soil Datasets')

    while count > 0 and (page-1*size < max):
        headers = {'Accept': 'application/json', "User-Agent": "Soilwise Harvest v0.1"}
        proceed = True
        records = []
        try:
            resp = requests.get(f"{url}?page={page}&size={size}",headers=headers)
            records = resp.json().get('data')
            max = resp.json().get('meta',{}).get("total_records",max)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            proceed = False
            print(f'Error fetching {url}?page={page}, {e}')
        if proceed: 
            cnt = 1
            
            count=len(records)
            for r in records: 
                print(f"{(page-1)*size+cnt}. {r.get('url',r.get('id'))}")
                cnt=cnt+1
                hashcode = hashlib.md5(str(r).encode("utf-8")).hexdigest() # get unique hash for html 
                id = r.get('url',r.get('id'))
                insertRecord(   identifier=stripdoi(id),
                                uri=r.get('url'),
                                identifiertype=tp(id),
                                title=r.get('title',''),
                                resulttype='JSON',
                                resultobject=str(r),
                                hashcode=hashcode,
                                source=label,
                                itemtype='dataset') # insert into db
        page = page+1
