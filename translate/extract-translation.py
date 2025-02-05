# Desc: script extracts from turtle if a translation can be added, then adds translation key to translation table
# Author: Paul van Genuchten
# License: MIT

from rdflib import Graph, Literal, URIRef, term
from rdflib.namespace import DC, DCTERMS, RDF, FOAF, SKOS
import json, os, psycopg2
from datetime import datetime, timedelta

import sys
sys.path.append('utils')
from database import dbQuery, insertSQL

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

translatableProperties = [DCTERMS.title,DCTERMS.description]
ISOPairs = {    
    "bg": {"code":"bul","label":"Bulgarian"},        
    "fr": {"code":"fre|fra","label":"French"},            
    "pl": {"code":"pol","label":"Polish"},    
    "cs": {"code":"cze|ces","label":"Czech"},            
    "hr": {"code":"hrv","label":"Croatian"},            
    "pt": {"code":"por","label":"Portuguese"},    
    "da": {"code":"dan","label":"Danish"},        
    "hu": {"code":"hun|mag","label":"Hungarian"},            
    "ro": {"code":"rum|ron","label":"Romanian"},    
    "de": {"code":"ger|deu","label":"German"},    
    "is": {"code":"ice|isl","label":"Icelandic"},        
    "ru": {"code":"rus","label":"Russian"},    
    "et": {"code":"est","label":"Estonian"},        
    "it": {"code":"ita","label":"Italian"},
    "sk": {"code":"slo|slk","label":"Slovak"},    
    "el": {"code":"gre|ell","label":"Greek"},    
    "lt": {"code":"lit","label":"Lithuanian"},    
    "sl": {"code":"slv","label":"Slovenian"},    
    "es": {"code":"spa|esp","label":"Spanish"},    
    "lv": {"code":"lav","label":"Latvian"},    
    "sv": {"code":"swe","label":"Swedish"},    
    "fi": {"code":"fin","label":"Finnish"},    
    "nl": {"code":"dut|nld","label":"Dutch"},
    "ch": {"code":"chi|zho", "label":"Chinese"},
    "ar": {"code":"ara|arb", "label": "Arabic"}, 
    "ja": {"code":"jap", "label": "Japanese"},
    "ga": {"code":"gle", "label": "Irish"},
    "nn": {"code":"nor", "label":"Norwegian"},
    "tr": {"code":"tur", "label":"Turkish"}
}

def isoMatch(lang):
    for k,v in ISOPairs.items():
        if lang.lower() == k or lang.lower() in v['code']:
            return k
    return None


def manageTrans(turtle,subject,prop,id,lang_source,lang_target="en"):
    lang_source = isoMatch(lang_source)
    if lang_source in [None,'']:
        lang_source = 'LD' # Language Detect

    # first get the untranslated string
    srctxt = None
    for s,p,o in turtle.triples((subject,prop,None)):
        if o.__class__ == term.Literal:
            srctxt = str(o) # use any language
            if isoMatch(o.language) == lang_source: # if default language
                srctxt = str(o)
                break

    if not srctxt:
        print('No source for {prop}:{lang_source}')
    else:
        # find a english translation
        hasENG = False
        for s,p,o in turtle.triples((subject,prop,None)):
            if o.language == 'en' and lang_source != 'LD': # translate anyway, because we don't knw source-lang
                hasENG = True
                # insert trans
                insertSQL('harvest.translations',
                        ['source','target','lang_source','lang_target','context','date_inserted'],
                        (srctxt,o,lang_source,lang_target,id,datetime.now()))
                break
    
        # prepare a translation for this record
        if not hasENG:
            # insert untranslated
            insertSQL('harvest.translations',
                    ['source','lang_source','lang_target','context','date_inserted'],
                    (srctxt,lang_source,lang_target,id,datetime.now()))



# get records which have language<>en and are not already translated
sql = '''select identifier,language,turtle from harvest.items 
    where not coalesce(language,'') = ''
    and not coalesce(turtle,'') = ''
    and not upper(language) = any(ARRAY['EN','ENG']) 
    and identifier not in (
        select coalesce(context,'') 
        from harvest.translations 
        where target is not null 
        OR date_inserted > (now() - interval '1 day')) 
    limit 250'''

recs = dbQuery(sql,(),True)

if recs:
    total = len(recs)
    counter = 0
    
    for rec in sorted(recs):
        identifier,language,turtle = rec

        g = Graph()
        g.parse(data=turtle, format='turtle')
        
        subject = None
        # combination of language and description are the objects we're interested in
        for s,p,o in g.triples((None,DCTERMS.description,None)):
            if (s, DCTERMS.language, None) in g:
                subject = s
                break
    
        if subject:
            if isoMatch(language) not in ['None','en','']:
                print(f"translations for {identifier} in {isoMatch(language)}")
                for p in translatableProperties:
                    manageTrans(g,subject,p,identifier,language)
        else:
            print('No language indicated for record')
