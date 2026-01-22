from dotenv import load_dotenv, json
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DC, DCAT, DCTERMS, SKOS, SDO, FOAF
import sys,time,hashlib,os
sys.path.append('utils')
from database import insertRecord, dbQuery

# Load environment variables from .env file
load_dotenv()

label = 'ISRIC-LIB'

def addNS(e):
    if e in DCTERMS:
        return DCTERMS[e]
    elif e in SDO:
        return SDO[e]
    elif e in DCAT:
        return DCAT[e]
    elif e in SKOS:
        return SKOS[e]
    elif e in FOAF:
        return FOAF[e]
    else:
        return None        

def dict2graph(d):
    g = Graph()
    r = None
    for i in d['identifier']:
        if i.startswith('http'):
            r = URIRef(i)
            break
    if r:
        for k,v in d.items():
            if isinstance(v, list):
                for i in v:
                    g.add((r,addNS(k),Literal(i)))
            else:
                g.add((r,addNS(k),Literal(v)))
    return g


# get non processed records from db
unparsed = dbQuery(f"select identifier,resultobject,resulttype,itemtype,uri from harvest.items where source = '{label}' and (turtle is Null or turtle = '')")

for rec in sorted(unparsed):
    rid,txt,restype,itemtype,uri = rec
    print(f'Parse {rid}')
    
    md = json.loads(txt)

    dsRDF = dict2graph(md)    
    triples = dsRDF.serialize(format='turtle') # todo: strip the namespaces?
    dbQuery(f"update harvest.items set turtle=%s where identifier=%s",(triples,rid),False)
