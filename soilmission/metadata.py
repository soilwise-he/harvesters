import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import sys,time,hashlib,os,json,re
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
            
            d=''
            try:
                d = r.get('header',{}).get('dri:dateOfCollection',{}).get('$','')
            except:
                None
            m = {}
            try:
                m = r.get('metadata',{}).get('oaf:entity',{}).get('oaf:result',{})
            except:
                None
            type = m.get('resulttype',{}).get('@classid','')
            title = m.get('title',{})
            if isinstance(title, list): # multilingual
                for t2 in title:
                    if t2.get('$') not in [None,'']: 
                        title = t2
                        break
            
            # remove html from title
            title = re.sub('<[^<]+?>', '', title.get('$','') )

            pid = None
            pids = m.get('pid',[])
            if not isinstance(pids, list):
                pids = [pids]
            for p in pids:
                if isinstance(p, dict):
                    if p.get('$'):
                        pid = p.get('$')
                        if p.get("classid") == "doi":
                            break
            if not pid:
                pid2 = m.get('originalId')
                if not isinstance(pid2, list):
                    pid2 = [pid2]
                for p in pid2:
                    if p.get('$'):
                        pid = p.get('$').split('|').pop().split('::').pop() # typical format 50|od______2659::df09b7a0eea847fe66dd338241c41415
                        if isinstance(p, dict) and (p.get('$','').startswith('http') or p.get('$','').startswith('10.') or p.get('$','').startswith('doi:')):
                            break

            if pid:
                ruri = str(pid)
                idtype = 'uuid'
                if ruri.startswith('10.'):
                    ruri = f'https://doi.org/{ruri}'
                elif ruri.startswith('doi:'):
                    ruri = f"https://doi.org/{ruri.split(':').pop()}"
                if 'doi.org/10.' in ruri:
                    idtype = 'doi'
                hashcode = hashlib.md5(json.dumps(r).encode("utf-8")).hexdigest() # get unique hash for json
                insertRecord(   identifier=str(pid),
                                uri=ruri,
                                identifiertype=idtype,
                                title=title,
                                resulttype='oaf',
                                resultobject=json.dumps(r.get("metadata",{}).get("oaf:entity",{}).get("oaf:result",{})),
                                hashcode=hashcode,
                                project=grant,
                                source=label,
                                itemtype=type)



    



    # insert doi into graph with source openaire

