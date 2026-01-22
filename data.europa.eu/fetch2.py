# fetches data from data.europa.eu based on inspire theme 'theme/so'

import requests

from dotenv import load_dotenv
import sys,time,hashlib,os,json
sys.path.append('utils')
from database import insertRecord, dbQuery, hasSource
from utils import doi_from_url, pid_type, to_schema_org
# Load environment variables from .env file
load_dotenv()

label = 'DATA.EUROPA.EU.BY.SOIL'

hasSource(label,'','','SPARQL')

# to do, run a query to get id hash on all records from this source, 
# to check if a record already exists, so doesn't need to be retrieved/inserted -> which will fail

pl = { "locale": "en", "query": """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?datasetURI ?datasetTitle ?dsId WHERE {
  
  VALUES ?soilConcept {
    <http://inspire.ec.europa.eu/theme/so>
    <http://eurovoc.europa.eu/100277>
    <http://data.europa.eu/cpv/cpv/14212400>
    <http://data.europa.eu/bna/c_87a129d9>
    <http://www.eionet.europa.eu/gemet/concept/7843>
    <http://aims.fao.org/aos/agrovoc/c_7156>
    "Soil" "soil"
  }
  ?datasetURI a dcat:Dataset ;
  dct:identifier ?dsId ;
  dct:title ?datasetTitle ;
  dcat:theme|dct:subject|dcat:keyword ?soilConcept .
  FILTER (LANG(?datasetTitle) = "" || CONTAINS(LANG(?datasetTitle), "en"))
} GROUP BY ?datasetURI ?datasetTitle"""
}

print('Query data.europa.eu')
resp = requests.post('https://data.europa.eu/sparql', data=pl, headers={'Accept': 'application/sparql-results+json'})

recs = resp.json().get('results',{}).get('bindings',[])
print(f'Result {len(recs)} records)')

for r in recs:
    id = doi_from_url(r.get('dsId',{}).get('value',''))
    uri = r.get('datasetURI',{}).get('value','')
    ttl = r.get('datasetTitle',{}).get('value','')

    r2 = {}
    for k,v in r.items():
        r2[k] = v.get('value','')

    hashcode = hashlib.md5(json.dumps(r2).encode("utf-8")).hexdigest() # get unique hash for html 
    insertRecord(   identifier=id,
                    identifiertype=pid_type(id),
                    itemtype='dataset',
                    uri=uri,
                    title=ttl,
                    resulttype='json',
                    resultobject=json.dumps(r2),
                    hashcode=hashcode,
                    source=label
                )