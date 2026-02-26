# fetches data from data.europa.eu based on inspire theme 'theme/so'

import requests
import time
from urllib.parse import urlparse
from dotenv import load_dotenv
import sys,time,hashlib,os,json
sys.path.append('utils')
from database import insQry, dbInit, hasSource
from utils import doi_from_url, pid_type, to_schema_org
# Load environment variables from .env file
load_dotenv()

label = 'DATA.EUROPA.EU.BY.SOIL'

hasSource(label,'','','SPARQL')
ENDPOINT = "https://data.europa.eu/sparql"
BASE = "https://data.europa.eu/api/hub/search/datasets"

session = requests.Session()

def get_label_or_trans(tk_):
  # get trans value
  if isinstance(tk_, list):
    no_empties = [j for j in tk_ if j not in [None,'']]
    if len(no_empties) < 2:
      return get_label_or_trans(next(iter(no_empties),''))
    tmp = []
    for i in no_empties:
      tmp.append(get_label_or_trans(i))
    return tmp
  elif isinstance(tk_, dict):
    for z in ['en','resource','id','label']:
      if z in tk_ and tk_[z] not in [None,'']:
        return tk_[z]
      else:
        return next(iter([f for f in tk_.values() if f not in [None,'']]),'')
  else:
     return tk_

def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

def get_detail(dataset_id):
    url = f"{BASE}/{dataset_id}"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def extract_id(uri):
    return uri.rstrip("/").split("/")[-1]

def run_query(query):
    r = requests.post(
        ENDPOINT,
        data={"query": query, "locale": "en"},
        headers={"Accept": "application/sparql-results+json,*/*;q=0.9", "Content-Type": "application/x-www-form-urlencoded"},
        timeout=60
    )
    r.raise_for_status()
    return r.json()["results"]["bindings"]


def initial():
  # to do, run a query to get id hash on all records from this source, 
  # to check if a record already exists, so doesn't need to be retrieved/inserted -> which will fail
  pl = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?URI ?identifier
WHERE {

  ?URI a dcat:Dataset ;
       dct:identifier ?identifier .

  {
    VALUES ?soilConcept {
      <http://inspire.ec.europa.eu/theme/so>
      <http://eurovoc.europa.eu/100277>
      <http://data.europa.eu/cpv/cpv/14212400>
      <http://data.europa.eu/bna/c_87a129d9>
      <http://www.eionet.europa.eu/gemet/concept/7843>
      <http://aims.fao.org/aos/agrovoc/c_7156>
      "Soil"
      "soil"
    }

    ?URI dcat:theme | dct:subject | dcat:keyword ?soilConcept .
  }
  UNION
  {
    ?URI dct:isPartOf <https://data.jrc.ec.europa.eu/collection/esdac> .
  }
}
"""

  recs=[]
  for r in run_query(pl):
     # check if uri is blanknode or already in recs, then use identifier
     uri = r.get("URI",{}).get("value")
     id = r.get("identifier",{}).get("value")
     if uri.startswith('nodeID://'):
        uri = None
     if not uri or uri in recs:
       #if id not in recs:
       #   recs.append(id)
       None
     else:      
       recs.append(uri)

  return recs


sparql_ids = initial()

records = []
for did in sparql_ids:
    try:
        print(did)
        rec = get_detail(extract_id(did))
        records.append(rec)
    except Exception as e:
        print("Failed:", did, e)

dbconn = dbInit()
with dbconn.cursor() as cur:
  for r2 in records:
    r = r2.get('result')
    if r:
      transkeys = "title,description,license,categories,spatial_resource,country,rights,format,access_right,landing_page,accrual_periodicity,keywords,provenance".split(',')
      r['catalog'] = r.get('catalog',{}).get('homepage',r.get('catalog',{}).get('id'))

      for k in transkeys:
        if k in r and r[k] is not None:
          r[k] = get_label_or_trans(r[k])
      mapping = {
        "id": "identifier",
        "resource": "@id",
        "catalog": "includedInDataCatalog",
        "categories": "keywords",
        "title": "name",
        "spatial_resource": "spatial",
        "country": "countryOfOrigin",
        "rights": "usageInfo",
        "format": "encodingFormat",
        "access_right": "conditionsOfAccess",
        "language": "inLanguage",
        "landing_page": "mainEntityOfPage"
        }
      # distributions
      if 'distributions' in r:
        dsts = []
        for d in r.pop("distributions"):
          dsts.append({
              "@type": "DataDownload",
              "contentUrl": ",".join(d.get('access_url','')),
              "name": get_label_or_trans(d.get('title','')),
              "encodingFormat": "https://www.iana.org/assignments/media-types/application/gml%2Bxml",
              "license": get_label_or_trans(d.get("license",''))
          })
        r['distribution'] = dsts

      if 'inLanguage' in r and isinstance(r['inLanguage'],list):
         r['inLanguage'] = next(iter(r['inLanguage']),'')
      # temporal

      # "temporal": [ {"gte": "2025-12-01T00:00:00Z", "lte": "2025-12-04T00:00:00Z"} ]
      if 'temporal' in r or "temporalCoverage" in r:
         tmp = r.get('temporalCoverage',r.get('temporal',[]))
         if isinstance(tmp,list):
            tmp = next(iter(tmp),{}) # use first
         if isinstance(tmp, dict):
            tmp = f"{tmp.get('gte','...')}/{tmp.get('lte','...')}"
      r["temporalCoverage"] = tmp

      # process contacts / translate agent to org/person
      for ct in ['author', 'publisher', 'creator', 'provider', 'funder']:
         if not isinstance(r.get(ct), list):
            r[ct] = [r.get(ct)]
         for c in r[ct]:
            if isinstance(c, dict):
              c['@type'] = "Organization" if c.get('type') == 'Agent' else "Person"
              c.pop('type', None)
  
      # quality_meas

      # spatial [{"type": "Polygon", "coordinates": [[[8.0381, 57.7536], [15.5724, 57.7536], [15.5724, 54.453], [8.0381, 54.453], [8.0381, 57.7536]]]}]
      if 'spatial' in r:
        geom = r['spatial']
        if isinstance(geom,list):
            geom = next(iter(geom),{}) # use first
        if isinstance(geom, dict) and "coordinates" in geom: 
          try:
              geom = {"@type": "GeoShape",
                      "polygon": [f'{c[1]} {c[0]}' for c in geom[0][0]]}
          except:
              print(f'{geom} is not an expected geometry')
              None
        r['spatial'] = geom
      
      r['@type'] = "Dataset"
      r.pop('translation_meta')
      r = to_schema_org(r, mapping)
      id_ = r.get('@id')
      #print(r.get('name',r.get('identifier','')))

      hashcode = hashlib.md5(json.dumps(r).encode("utf-8")).hexdigest() # get unique hash for html 
      values = {
          'identifier': doi_from_url(id_),
          'identifiertype': pid_type(doi_from_url(id_)),
          'uri': r.get('@id',''),
          'resultobject': json.dumps(r),
          'resulttype': 'json',
          'hash': hashcode,
          'source': label,
          'itemtype':'dataset',
          'title': r.get('name','')
      }

      try:
        insQry('harvest.items',values,cur)        
      except Exception as e:
        print(f"Error: {str(e)}")

dbconn.commit()   
dbconn.close()