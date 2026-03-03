import requests, yaml
import xml.etree.ElementTree as ET
from itertools import islice
from dotenv import load_dotenv
import json, sys, hashlib, os
sys.path.append('utils')
from database import insQry, dbInit, hasSource
from utils import doi_from_url, pid_type, to_schema_org

# Load environment variables from .env file
load_dotenv()

SPARQL_ENDPOINT = "https://cordis.europa.eu/datalab/sparql"
BATCH_SIZE = 10
SOURCE = "CORDIS"

# -------------------------------------------------
# Fetch project identifiers in batches
# -------------------------------------------------
def fetch_project_ids():
    dbconn = dbInit()
    with dbconn.cursor() as cur:
        cur.execute("SELECT grantnr FROM harvest.projects where coalesce(grantnr, '') != ''")
        rows = [r[0] for r in cur.fetchall()]
    dbconn.commit()   
    dbconn.close()
    return rows 
    

def batched(iterable, size):
    it = iter(iterable)
    while True:
        batch = list(islice(it, size))
        if not batch:
            break
        yield batch

# -------------------------------------------------
# Build SPARQL query dynamically
# -------------------------------------------------
def build_sparql_query(project_ids):
    quoted = ", ".join(f"\"{pid}\"" for pid in project_ids)
    return f"""
PREFIX eurio: <http://data.europa.eu/s66#>

SELECT DISTINCT
  ?projectId
  ?title
  ?abstract
  ?acronym
  ?startDate
  ?endDate
  ?totalCost
  ?doi
  ?prjWebsite
  ?organisationName
  ?roleLabel
  ?orgCountry
  ?orgCity
  ?orgAddress
  ?postalCode
  ?orgWebsite
  ?longitude
  ?latitude
WHERE {{
  ?project a eurio:Project ;
           eurio:identifier ?projectId ;
           eurio:title ?title .
  
  FILTER(?projectId IN ({quoted}))

  OPTIONAL {{ ?project eurio:startDate ?startDate }}
  OPTIONAL {{ ?project eurio:endDate ?endDate }}
  OPTIONAL {{ ?project eurio:doi ?doi }}
  OPTIONAL {{ ?project eurio:abstract ?abstract }}
  OPTIONAL {{ ?project eurio:url ?prjWebsite }}
  
  ?project eurio:hasInvolvedParty ?role .
  ?role eurio:roleLabel ?roleLabel ;
        eurio:isRoleOf ?org .
  ?org eurio:legalName ?organisationName .

  OPTIONAL {{
    ?acr a eurio:Acronym ;
         eurio:shortForm ?acronym ;
         eurio:isAcronymOf ?project .
  }}
  
  OPTIONAL {{
    ?project eurio:isFundedBy ?grant .
    ?grant eurio:hasFundingAmount ?fa .
    ?fa eurio:value ?totalCost 
  }}
  
OPTIONAL {{
  ?org eurio:url ?orgWebsite .
  ?org eurio:hasSite ?site .
  ?site a eurio:Site .

  ?site eurio:hasAddress ?addr .
  ?addr a eurio:PostalAddress .

  OPTIONAL {{ ?addr eurio:streetAddress ?orgAddress }}
  OPTIONAL {{ ?addr eurio:postalCode ?postalCode }}
  OPTIONAL {{ ?addr eurio:addressLocality ?orgCity }}
  OPTIONAL {{ ?addr eurio:addressCountry ?orgCountry }}
    
  ?site eurio:hasCoordinates ?coords .
  OPTIONAL {{ ?coords eurio:longitude ?longitude }}   
  OPTIONAL {{ ?coords eurio:latitude ?latitude }}   
}}
  
}}
ORDER BY ?projectId ?organisationName
"""

# -------------------------------------------------
# Execute SPARQL
# -------------------------------------------------
def run_sparql(query):
    headers = {
        "Accept": "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "SoilWiseHarvester/1.0 (contact: info@soilwise-he.eu)"
    }

    response = requests.post(
        SPARQL_ENDPOINT,
        data={"query": query},
        headers=headers,
        timeout=60
    )

    response.raise_for_status()
    return response.json()["results"]["bindings"]

# -------------------------------------------------
# Build DC project objects
# -------------------------------------------------
def build_projects(rows):
    projects = {}

    for r in rows:
        
        pid = f"10.3030/{r['projectId']['value']}"
        
        if pid not in projects:
            # let's create mcf instead
            projects[pid] = {
                "mcf":{"version": "1.0"},
                "metadata":{
                    "identifier": pid,
                    "hierarchylevel": "project",
                    "language": "eng",
                    "dataseturi": r.get("doi", {}).get("value",f"http://doi.org/10.3030/{pid}")
                },
                "identification":{
                    "title": r["title"]["value"],
                    "abstract": r.get("abstract", {}).get("value", ""), 
                    "extents": {
                        "temporal": [{
                            "begin": r.get("startDate", {}).get("value"),
                            "end": r.get("endDate", {}).get("value")
                        }]
                    }
                },
                "contacts": {},
            }
            if 'acronym' in r:
                projects[pid]['metadata']["additional_identifiers"] = [{
                        "identifier": r.get("acronym", {}).get("value", ""),
                        "scheme": "acronym"
                    }]
            if 'prjWebsite' in r:
                projects[pid]['distribution'] = {
                    "www": {
                        "url": r.get("prjWebsite", {}).get("value",''),
                        "type": "website"
                    }}
                projects[pid]['identification']['url'] = r.get("prjWebsite", {}).get("value",'')
                

        org = {
            "organization": r["organisationName"].get('value','').capitalize(),
            "role": r["roleLabel"]["value"].lower(),
        }
        if 'orgAddress' in r:
            org['address'] = r.get("orgAddress", {}).get("value",'').capitalize()
        if 'postalCode' in r:
            org['postalcode'] = r.get("postalCode", {}).get("value",'')
        if 'orgWebsite' in r:
            org['url'] = r.get("orgWebsite", {}).get("value",'')
        if 'longitude' in r:
            org['longitude'] = r.get("longitude", {}).get("value",'')
        if 'latitude' in r:
            org['latitude'] = r.get("latitude", {}).get("value",'')
        if 'orgCity' in r:
            org['city'] = r.get("orgCity", {}).get("value",'')
        if 'orgCountry' in r:
            org['country'] = r.get("orgCountry", {}).get("value",'')

        projects[pid]["contacts"][f"c{len(projects[pid]['contacts'])}"] = org

    return projects


# -------------------------------------------------
# Persist mcf
# -------------------------------------------------
def store_documents(projects):
    dbconn = dbInit()
    with dbconn.cursor() as cur:

        for pid, mcf in projects.items():
            try:

                hashcode = hashlib.md5(yaml.dump(mcf, sort_keys=False).encode("utf-8")).hexdigest() # get unique hash for html 
                values = {
                    'identifier': doi_from_url(pid),
                    'identifiertype': pid_type(doi_from_url(pid)),
                    'uri': pid,
                    'resultobject': yaml.dump(mcf, sort_keys=False),
                    'resulttype': 'yaml',
                    'hash': hashcode,
                    'source': SOURCE,
                    'itemtype':'project',
                    'title': mcf.get('identification',{}).get('title','')
                }
                insQry('harvest.items',values,cur)        
            except Exception as e:
                print(f"Error record {pid}: {str(e)}")   

    dbconn.commit()   
    dbconn.close()

# -------------------------------------------------
# Main ETL loop
# -------------------------------------------------
if __name__ == "__main__":
    # add source, if it does not exist yet
    hasSource(SOURCE)

    project_ids = fetch_project_ids()

    for batch in batched(project_ids, BATCH_SIZE):
        query = build_sparql_query(batch)
        rows = run_sparql(query)
        projects = build_projects(rows)
        store_documents(projects)
        print(f"Processed batch: {batch}")

    print("ETL completed successfully.")