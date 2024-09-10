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

def manageTrans(gr,ky,id,ln):
    # first get the untranslated string
    src = None
    for s,p,o in gr.triples((None,ky,None)):
        src = str(o)
        if o.language.lower() == ln.lower(): #(3-letter vs 2-letter?)
           src = str(o) 
           break

    hasENG = False
    for s,p,o in gr.triples((None,ky,None)):
        if o.language == 'en':
            hasENG = True
            # insert trans

    if not hasENG:
        # insert untranslated
        dbQuery(f'insert into translations () values()',False)

# get records which have language<>en and are not already translated
sql = '''select identifier,language,turtle from harvest.items 
where not coalesce(language,'') = ''
and not coalesce(turtle,'') = ''
and not upper(language) = any(ARRAY['EN','ENG']) 
and identifier not in (select coalesce(context,'') from harvest.translations) 
limit 5'''

recs = dbQuery(sql)

if recs:
    total = len(recs)
    counter = 0
    print(total)
    
    for rec in sorted(recs):
        identifier,language,turtle = rec

        g = Graph()
        g.parse(data=turtle, format='turtle')
        manageTrans(g,DCTERMS.title,identifier,language)
        manageTrans(g,DCTERMS.description,identifier,language)
