import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import sys,time,hashlib,os,json,re
sys.path.append('utils')
from database import insertRecord, dbQuery, hasSource
from utils import doi_from_url, pid_type
# Load environment variables from .env file
load_dotenv()


OAurl = 'https://api.openaire.eu/graph/v2/researchProducts'
DCurl = 'https://api.datacite.org/dois/'
CrossUrl = ''


# get project ids from 
recs = dbQuery("SELECT identifier, uri, hash FROM harvest.vw_unique_harvest_items where identifiertype = 'doi' and doimetadata is null LIMIT 100")

# for each record, get openaire doi's    
for rec in sorted(recs):  

    headers = { "User-Agent": "Soilwise Harvest v0.1" }
    identifier, uri, hash = rec
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
                d = m.get('dateOfCollection','')
                title = m.get('mainTitle',{})
                if isinstance(title, list): # multilingual
                    for t2 in title:
                        if t2.get('$') not in [None,'']: 
                            title = t2
                            break
                # remove html from title
                title = re.sub('<[^<]+?>', '', title )

                dbQuery(f"update harvest.items set doimetadata=%s where hash=%s",(json.dumps(m),hash),False)     
        
        else: # try doi registry
            print('try doi registry')
            headers['Accept'] = 'application/citeproc+json'    
            uri2 = "https://dx.doi.org/" + identifier.split(':').pop().split('/').pop()  
            jsonResp = None
            try:
                response = requests.get(uri2,headers=headers)
                response.raise_for_status()
                jsonResp = response.json()
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}')
            if jsonResp:
                dbQuery(f"update harvest.items set doimetadata=%s where hash=%s",(json.dumps(jsonResp),hash),False) 
            else:
                print('Failed parsing doi')
                dbQuery(f"update harvest.items set doimetadata=%s where hash=%s",(f'Failed parsing doi',hash),False) 
        

