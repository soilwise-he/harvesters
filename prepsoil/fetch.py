import requests

from dotenv import load_dotenv
import sys,time,hashlib,os,json
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
    # elif 'geonetwork' in id:
    #    return 'uuid'
    elif id.startswith('http'):
        return 'uri'
    else:
        return 'uuid'

label = "PREPSOIL"

if os.environ.get("HARVESTTYPES"):
    harvesttypes = os.environ.get("HARVESTTYPES").split(',')
else:
    harvesttypes = ['document'] #,'lllh']

# harvest   publications
if 'document' in harvesttypes:
    url="https://prepsoil.eu/api/knowledge-hub"
    # add source if it does not exist
    hasSource(label,url,'',label)
    proceed = True
    print('PrepSoil Publications')
    headers = {'Accept': 'application/json', "User-Agent": "Soilwise Harvest v0.1"}
    records = []
    try:
        resp = requests.get(f"{url}",headers=headers)
        records = resp.json()
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        proceed = False
        print(f'Error fetching {url}, {e}')
    
    if proceed: 
        count=len(records)
        for r in records: 
            id = r.get('field_link_external_resource').strip()
            if id.startswith('http'):
                print(id)
                hashcode = hashlib.md5(json.dumps(r).encode("utf-8")).hexdigest() # get unique hash for html 
                insertRecord(   identifier=stripdoi(id),
                                uri=id,
                                identifiertype=tp(id),
                                title=r.get('title',''),
                                resulttype='JSON',
                                resultobject=json.dumps(r),
                                hashcode=hashcode,
                                source=label,
                                itemtype='document') # insert into db

