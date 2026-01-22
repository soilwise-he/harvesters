import requests

from dotenv import load_dotenv
import sys,time,hashlib,os,json
sys.path.append('utils')
from database import insertRecord, dbQuery, hasSource
from utils import doi_from_url, pid_type, to_schema_org
# Load environment variables from .env file
load_dotenv()

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
                r['@id'] = id
                hashcode = hashlib.md5(json.dumps(r).encode("utf-8")).hexdigest() # get unique hash for html 
                dcmapping = {
                    "title": "name",
                    "field_country_select": "spatial",
                    "field_language": "language",
                    "field_media_format": "format",
                    "field_soil_qualities_properties": "about",
                    "field_link_external_resource": "url",
                    "field_name_external_resource": "source",
                    "field_soil_mission_objectives": "keywords",
                    "field_source": "source",
                    "field_sustainable_practices": "keywords",
                    "field_t_content": "@type"
                }
                r2 = to_schema_org(r, dcmapping)

                insertRecord(   identifier=r2['identifier'], 
                                uri=r2.get('url',r2['identifier']), 
                                identifiertype=pid_type(r2['identifier']),
                                title=r2.get('title',''),
                                resulttype='JSON',
                                resultobject=json.dumps(r2),
                                hashcode=hashcode,
                                source=label,
                                itemtype=r2.get('type','document')[:50]) # insert into db

