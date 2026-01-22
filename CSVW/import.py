import requests
from dotenv import load_dotenv
import sys, time, hashlib, os, json
from csvwlib import CSVWConverter
from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, SKOS, DCTERMS, SCHEMA

DCAT = Namespace('http://www.w3.org/ns/dcat#')

sys.path.append('utils')
from database import insertRecord, dbQuery, hasSource
# Load environment variables from .env file
load_dotenv()

url = os.environ.get("HARVEST_URL")
if not url:
    print('env HARVEST_URL not set')
    exit
else:
    print('harvest', url)

label = os.environ.get("HARVEST_LABEL").upper() or url
# add source if it does not exist
hasSource(label,url,'',label)

# run the csvwlib to fetch the csv as kg
records = CSVWConverter.to_rdf(None, url, mode='standard')

if records:
    # for each dataset in knowledge graph
    # to understand if the proper distributions/contacts are included in each graph-fragment
    # or maybe a mcf conversion should already be applied
    for s, p, o in records.triples((None, RDF.type, (DCAT.Dataset, DCAT.DataService, DCAT.Resource, SCHEMA.Dataset, SCHEMA.Article, DCTERMS.Resource))):

        ttl = r.get('title',{}).get('en','')
        hashcode = hashlib.md5(json.dumps(r).encode("utf-8")).hexdigest() # get unique hash for html 
        insertRecord(   identifier=id,
                        identifiertype='uuid',
                        title=ttl,
                        resulttype='JSON',
                        resultobject=sg.serialize(format="ttl"),
                        hashcode=hashcode,
                        source=label,
                        itemtype='dataset') # insert into db






