
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DC, DCTERMS, RDF, FOAF, SKOS
import traceback,urllib
import json, os, psycopg2
import requests

import sys
sys.path.append('../utils')
from database import dbQuery

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

TRANSAPIURL = os.environ.get('TRANSAPIURL') or False

def trans(txt,identifier,lang_source):
    mytr = {"lang_source": lang_source,
            "lang_target": "en",
            "source": txt,
            'context': identifier }
    return requests.post(TRANSAPIURL, json=mytr)



# get records to be translated, not already translated and having a language!english
recs = dbQuery("""select identifier, title, abstract, lineage, language 
                    from public.records
                    where identifier not in (select context from harvest.translations)
                    and language is not null 
                    and lower(language) <> "eng"
				    limit 5""")

if recs:
    total = len(recs)
    counter = 0
    
    for rec in sorted(recs):
        identifier, title, abstract, lineage, language = rec
        if title not in [None,'']:
            trans(title, identifier, language)
        if abstract not in [None,'']:
            trans(abstract, identifier, language)
        if lineage not in [None,'']:
            trans(lineage, identifier, language)