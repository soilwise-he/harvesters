



import requests

from dotenv import load_dotenv
import sys,time,hashlib,os,json
sys.path.append('utils')
from database import insertRecord, dbQuery, hasSource
# Load environment variables from .env file
load_dotenv()

label = "DATA.EUROPA.EU"

url='https://data.europa.eu/api/hub/search/search'
filter='?q=&filter=dataset&facets={"keywords":["soil","sol","boden","bodem","suelo","solo"]}'
# &includes=id,title.en,description.en,languages,modified,issued,distributions.access_url,distributions.format.label,distributions.format.id,distributions.license,distributions.description.en,categories.label,keywords.id,publisher,subjects,provenance

# add source if it does not exist
hasSource(label,url,'',label)

print(label,'datasets')
headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 
           "User-Agent": "Soilwise Harvest v0.1"}
proceed = True

records = []

p=0 # page
l=100 # limit
count=1000 # initial value, updated from result
maxp=100 # max pages for development only

while p < maxp and p * l < count:

    aUrl = f"{url}{filter}&page={p}&limit={l}"
    resp = requests.get(aUrl, headers=headers)
    resp = resp.json()
    count = resp.get('result',{}).get('count', 1000)
    records = resp.get('result',{}).get('results',[])
    print(p,p*l,len(records))
    p=p+1

    for r in records: 
        id = r.get('identifier',r.get('id'))
        if isinstance(id, list) and len(id) > 0 and len(id) > 0 and id[0]:
            id = id[0]
        else:
            id = r.get('id')
        # data.europe.eu adds a organisation to each identifier to prevent id conflicts, strip it
        id = id.split('@')[0]
        ttl = r.get('title',{}).get('en','')
        hashcode = hashlib.md5(json.dumps(r).encode("utf-8")).hexdigest() # get unique hash for html 
        insertRecord(   identifier=id,
                        identifiertype='uuid',
                        title=ttl,
                        resulttype='JSON',
                        resultobject=json.dumps(r),
                        hashcode=hashcode,
                        source=label,
                        itemtype='dataset') # insert into db






