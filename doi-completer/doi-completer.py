import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import sys,time,hashlib,os,json,re
sys.path.append('utils')
from database import dbQuery, dbInit, insQry
from utils import doi_from_url, pid_type,pid_from_url,is_doi
# Load environment variables from .env file
load_dotenv()

OAurl = 'https://api.openaire.eu/graph/v2/researchProducts'
DCurl = 'https://api.datacite.org/dois/'
CrossUrl = ''

# todo: run doi completer for a single source only

# get doi metadata, prevent failed
# doi is either 10.xxx/yyy.zzz or https://doi.org/10.xxx/yyy.zzz
recs = dbQuery('''SELECT regexp_replace(identifier, '^.*?doi\\.org/', '') AS pid, uri, hash 
               FROM harvest.vw_unique_harvest_items 
               where (
                identifiertype = 'doi'
               OR 
                (identifiertype = 'uri' and identifier like '%%doi.org%%')
               )
               and source <> 'OPENAIRE' 
               and coalesce (error,'') = ''
               and regexp_replace(identifier, '^.*?doi\\.org/', '') not in (select identifier from harvest.items where source='OPENAIRE')
               LIMIT 500''')

# todo: how do we identify if updated record is available in openaire?

print(f'Parse {len(recs)} unparsed dois')

dbconn = dbInit()
with dbconn.cursor() as cur:

    # for each record, get openaire doi's    
    for rec in sorted(recs):  
        err2 = None
        hasFound = None
        headers = { "User-Agent": "Soilwise Harvest v0.1" }
        identifier2, uri, hash = rec
        # make sure doi does not include http (are other pids supported?)
        identifier = pid_from_url(identifier2) 
        # see if valid doi from pattern
        if not is_doi(identifier):
            print('no doi',identifier)
            dbQuery(f"update harvest.items set error=%s where hash=%s",(f'no doi; {identifier}',hash),False) 
            continue
        url=OAurl+'?pid='+identifier  
        print('parse id ',identifier)
        jsonResponse = None
        try:
            response = requests.get(url)
            response.raise_for_status()
            jsonResponse = response.json()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        if jsonResponse:
            matches = jsonResponse.get('results',[])
            header = jsonResponse.get('header',{})
            numFound = header.get('numFound',0)
            if numFound > 0:
                for m in matches:
                    hasFound = m
                    break
            
        if not hasFound:
            print('try doi registry')
            headers['Accept'] = 'application/citeproc+json'    
            uri2 = "https://dx.doi.org/" + identifier  
            jsonResp = None

            try:
                response = requests.get(uri2, headers=headers)
                response.raise_for_status()
                jsonResp = response.json()
            except HTTPError as http_err:
                err2 = str(http_err)
            except Exception as err:
                err2 = str(err)

        if hasFound:
            hashcode = hashlib.md5(json.dumps(hasFound).encode("utf-8")).hexdigest() # get unique hash for json
            values = { 'identifier': identifier,
                        'identifiertype': 'doi',
                        'uri': "https://doi.org/" + identifier,
                        'resulttype': 'openaire',
                        'resultobject': json.dumps(hasFound),
                        'doimetadata': json.dumps(hasFound),
                        'hash': hashcode,
                        'source': 'OPENAIRE',
                        'itemtype': hasFound.get('type','') }  
            insQry('harvest.items', values, cur) 
        else:        
            print(f'Failed parsing doi, {err2}')
            dbQuery(f"update harvest.items set error=%s where hash=%s",(f'Failed parsing doi {identifier}; {err2}',hash),False) 
        
dbconn.commit()   
dbconn.close()