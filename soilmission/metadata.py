import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import sys,time,hashlib,os,json
sys.path.append('utils')
from database import insertRecord, dbQuery, hasSource
# Load environment variables from .env file
load_dotenv()

label = 'OPENAIRE'
iurl = 'https://api.openaire.eu/search'
headers = { "User-Agent": "Soilwise Harvest v0.1" }
# add source if it does not exist
hasSource(label,iurl,'',label)

# get project ids from 
recs = dbQuery("select code, grantnr from harvest.projects where grantnr is not null")

# for each project, get openaire doi's    
for rec in sorted(recs):    
    code, grant = rec
    url='https://api.openaire.eu/search/researchProducts?projectID='+grant+'&format=json&size=500'
    try:
        response = requests.get(url)
        response.raise_for_status()
        # access JSOn content
        jsonResponse = response.json()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    if jsonResponse:
        matches = jsonResponse.get('response',{}).get('results',{})
        if not matches: # happens if query result is None
            matches = {}
        matches2 = matches.get('result',[])
    
        print('project',grant,':',code,'nr of records',len(matches2))
        for r in matches2:
            d = r.get('header',{}).get('dri:dateOfCollection',{}).get('$','')
            m = r.get('metadata',{}).get('oaf:entity',{}).get('oaf:result',{})
            type = m.get('resulttype',{}).get('@classid','')
            title = m.get('title',{})
            if isinstance(title, list): # multilingual
                title = title[0]
            title = title.get('$','')
            pid = None
            for p in m.get('pid',[]):
                if isinstance(p, dict) and p.get('@classid') == 'doi':
                    pid = p.get('$','')
                #else:
                #    print('Warning: failed parsing as dict',p)
            if pid:
                hashcode = hashlib.md5(json.dumps(r).encode("utf-8")).hexdigest() # get unique hash for json
                insertRecord(   identifier=pid,
                                uri='https://doi.org/'+pid,
                                identifiertype='doi',
                                title=title,
                                resulttype='JSON',
                                resultobject=json.dumps(r),
                                hashcode=hashcode,
                                project=grant,
                                source=label,
                                itemtype=type)



    



    # insert doi into graph with source openaire

