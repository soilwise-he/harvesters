import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import sys,time,hashlib,os,json,re
sys.path.append('utils')
from database import insQry, dbQuery, hasSource, dbInit
from utils import doi_from_url, pid_type
# Load environment variables from .env file
load_dotenv()

label = 'OPENAIRE'
iurl = 'https://api.openaire.eu/graph/v2/researchProducts'
headers = { "User-Agent": "Soilwise Harvest v0.1" }
# add source if it does not exist
hasSource(label,iurl,'',label)

# get project ids from 
recs = dbQuery("select code, grantnr from harvest.projects where grantnr is not null")

# for each project, get openaire doi's    

dbconn = dbInit()
with dbconn.cursor() as cur:

    for rec in sorted(recs):  
        code, grant = rec
        print('project',grant,':',code)
        if not grant in [None,'']:
            numFound = 1000 # (initial should be higher then actual number to enter loop)
            page = 1
            pageSize = 100
            while numFound > (page-1) * pageSize:   
                url=iurl+'?relProjectCode='+grant+'&pageSize=' + str(pageSize) + '&page=' + str(page)    
                jsonResponse = None
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
                    matches = jsonResponse.get('results',[])
                    header = jsonResponse.get('header',{})
                    numFound = header.get('numFound', 0)
                    print('- Page',page, 'nr of records', len(matches)+pageSize*(page-1) ,'/', numFound)
                    page = header.get('page',page) + 1
                    for m in matches:
                        d = m.get('dateOfCollection','')
                        title = m.get('mainTitle',{})
                        if isinstance(title, list): # multilingual
                            for t2 in title:
                                if t2 not in [None,'']: 
                                    title = t2
                                    break
                        
                        # remove html from title
                        if title not in [None,'']:
                            title = re.sub('<[^<]+?>', '', title )

                        pid = None
                        pids = m.get('pids',[])
                        if not isinstance(pids, list):
                            pids = [pids]
                        for p in pids:
                            if isinstance(p, dict):
                                if p.get('scheme','') =='doi':
                                    pid = p.get('value')
                                    break                            
                        if not pid:
                            oids = m.get('originalIds')
                            if isinstance(oids, list) and len(oids) > 0:
                                oids = oids[0]
                            pid = oids

                        if not pid:
                            pid = m.get('id','')        
                            
                        if pid:
                            ruri = str(pid)
                            hashcode = hashlib.md5(json.dumps(m).encode("utf-8")).hexdigest() # get unique hash for json
                            values = { 'identifier': doi_from_url(pid),
                                        'identifiertype': pid_type(doi_from_url(pid)),
                                        'uri': ruri,
                                        'title': title,
                                        'resulttype': 'openaire',
                                        'resultobject': json.dumps(m),
                                        'doimetadata': json.dumps(m),
                                        'hash':hashcode,
                                        'project':grant,
                                        'source':label,
                                        'itemtype':m.get('type','') }         

                            try:
                                insQry('harvest.items',values,cur)        
                            except Exception as e:
                                print(f"Error: {str(e)}")
        # at end of every project, commit to database
        dbconn.commit()   

dbconn.close()


# insert doi into graph with source openaire

