# fetches data from data.europa.eu based on inspire theme 'theme/so'

import requests
import time

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


def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]


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

  SELECT ?URI ?identifier ?title WHERE {
    
    VALUES ?soilConcept {
      <http://inspire.ec.europa.eu/theme/so>
      <http://eurovoc.europa.eu/100277>
      <http://data.europa.eu/cpv/cpv/14212400>
      <http://data.europa.eu/bna/c_87a129d9>
      <http://www.eionet.europa.eu/gemet/concept/7843>
      <http://aims.fao.org/aos/agrovoc/c_7156>
      "Soil" "soil"
    }
    ?URI a dcat:Dataset ;
    dct:identifier ?identifier ;
    dct:title ?title ;
    dcat:theme|dct:subject|dcat:keyword ?soilConcept .
    FILTER(LANG(?title) = "en")
  } GROUP BY ?URI ?title ?identifier LIMIT 20"""

  return [b["URI"]["value"] for b in run_query(pl)]


def detail(recs):
  DETAIL_QUERY = """
PREFIX dcat:   <http://www.w3.org/ns/dcat#>
PREFIX dct:    <http://purl.org/dc/terms/>
PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
PREFIX skos:   <http://www.w3.org/2004/02/skos/core#>
PREFIX schema: <http://schema.org/>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>

SELECT
  ?dataset

  (SAMPLE(?title_en) AS ?title)
  (SAMPLE(?desc_en) AS ?description)
  (SAMPLE(?prov_en) AS ?provenance)
  (GROUP_CONCAT(DISTINCT ?topic; separator=" | ") AS ?subject)
  (SAMPLE(?creator) AS ?creator)
  (SAMPLE(?publisher) AS ?publisher)
  (SAMPLE(?rightsHolder) AS ?rightsHolder)
  (SAMPLE(?createdDate) AS ?createdDate)
  (SAMPLE(?language) AS ?language)
  (SAMPLE(?spatialLabel) AS ?spatial)
  (GROUP_CONCAT(DISTINCT ?distributionURL; separator=" | ") AS ?distributionURLs)
  (GROUP_CONCAT(DISTINCT ?mediaType; separator=" | ") AS ?formats)
  (GROUP_CONCAT(DISTINCT ?license; separator=" | ") AS ?licenses)

WHERE {
  VALUES ?dataset { %s }

  # -------------------------
  # TITLE (prefer EN)
  # -------------------------
  OPTIONAL {
    ?dataset dct:title ?title .
    FILTER(LANG(?title) = "en" || LANG(?title) = "")
    BIND(?title AS ?title_en)
  }

  # -------------------------
  # DESCRIPTION (prefer EN)
  # -------------------------
  OPTIONAL {
    ?dataset dct:description ?desc .
    FILTER(LANG(?desc) = "en" || LANG(?desc) = "")
    BIND(?desc AS ?desc_en)
  }

  # -------------------------
  # PROVENANCE (literal statement, prefer EN)
  # -------------------------
  OPTIONAL {
    ?dataset dct:provenance ?provNode .

    # Sometimes provenance is literal already
    OPTIONAL {
      FILTER(isLiteral(?provNode))
      BIND(?provNode AS ?prov_en)
    }

    # Sometimes it is a node with label
    OPTIONAL {
      FILTER(isIRI(?provNode) || isBlank(?provNode))
      ?provNode rdfs:label|skos:prefLabel|dct:description ?provLit .
      FILTER(LANG(?provLit) = "en" || LANG(?provLit) = "")
      BIND(?provLit AS ?prov_en)
    }
  }

  # -------------------------
  # 🏷 SUBJECTS + KEYWORDS (combined)
  # -------------------------
  OPTIONAL {
    # Keywords (already literals)
    ?dataset dcat:keyword ?kw .
    FILTER(LANG(?kw) = "en" || LANG(?kw) = "")
    BIND(?kw AS ?topic)
  }

  OPTIONAL {
    # Subjects can be URIs or literals
    ?dataset dct:subject ?sub .

    # Literal subject
    OPTIONAL {
      FILTER(isLiteral(?sub))
      FILTER(LANG(?sub) = "en" || LANG(?sub) = "")
      BIND(?sub AS ?topic)
    }

    # URI subject → label
    OPTIONAL {
      FILTER(isIRI(?sub))
      ?sub skos:prefLabel|rdfs:label ?subLabel .
      FILTER(LANG(?subLabel) = "en" || LANG(?subLabel) = "")
      BIND(?subLabel AS ?topic)
    }
  }


  # -------------------------
  # AGENTS
  # -------------------------
  OPTIONAL { ?dataset dct:creator/(foaf:name|skos:prefLabel) ?creator }
  OPTIONAL { ?dataset dct:publisher/(foaf:name|skos:prefLabel) ?publisher }
  OPTIONAL { ?dataset dct:rightsHolder/(foaf:name|skos:prefLabel) ?rightsHolder }

  # -------------------------
  # DATE FALLBACK
  # -------------------------
  OPTIONAL { ?dataset dct:created|dct:issued|dct:modified ?createdDate }

  OPTIONAL { ?dataset dct:language ?language }

  # -------------------------
  # LICENSE / RIGHTS
  # -------------------------
  OPTIONAL {
    ?dataset dct:license ?lic .
    OPTIONAL { ?lic foaf:name|skos:prefLabel|dct:title ?licLabel }
  }
  OPTIONAL { ?dataset dct:accessRights ?accessRights }
  OPTIONAL { ?dataset dct:rights ?rights }
  BIND(COALESCE(?lic, ?licLabel, ?accessRights, ?rights) AS ?license)

  # -------------------------
  # DISTRIBUTIONS
  # -------------------------
  OPTIONAL {
    ?dataset dcat:distribution ?dist .
    OPTIONAL { ?dist dcat:downloadURL|dcat:accessURL|dcat:endpointURL|dcat:landingPage ?distributionURL }
    OPTIONAL { ?dist dcat:mediaType|dct:format ?mediaType }
  }

  # -------------------------
  # SPATIAL → literal from node
  # -------------------------
  OPTIONAL {
    ?dataset dct:spatial ?spatialNode .
    OPTIONAL {
      ?spatialNode skos:prefLabel|rdfs:label ?spatialLabel .
      FILTER(LANG(?spatialLabel) = "en" || LANG(?spatialLabel) = "")
    }
  }
}
GROUP BY ?dataset
"""
  aqry = DETAIL_QUERY % recs
  print(aqry)
  return run_query(aqry)

all_rows = []

records = initial()

for batch in chunked(records, 1):
    subset = detail(" ".join(f"<{uri}>" for uri in batch))
    all_rows.extend(subset)

#dbconn = dbInit()
#with dbconn.cursor() as cur:
for r in all_rows:
  print(r)

      # id = doi_from_url(r.get('identifier',{}).get('value',''))
      # uri = r.get('URI',{}).get('value','')
      # ttl = r.get('title',{}).get('value','')

      # r2 = {}
      # for k,v in r.items():
      #     r2[k] = v.get('value','')

      # hashcode = hashlib.md5(json.dumps(r2).encode("utf-8")).hexdigest() # get unique hash for html 

      # values = {
      #     'identifier': id,
      #     'identifiertype': pid_type(id),
      #     'uri': uri,
      #     'resultobject': json.dumps(r2),
      #     'resulttype': 'json',
      #     'hash': hashcode,
      #     'source': label,
      #     'itemtype':'dataset',
      #     'title': ttl
      # }

      # #try:
      # insQry('harvest.items',values,cur)        
      #except Exception as e:
      #    print(f"Error: {str(e)}")

#dbconn.commit()   
#dbconn.close();