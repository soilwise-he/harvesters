# parse imported html from esdac


from dotenv import load_dotenv
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DC, DCAT, DCTERMS, SKOS, SDO, FOAF
import sys,time,hashlib,os,json
sys.path.append('utils')
from database import insertRecord, dbQuery

# Load environment variables from .env file
load_dotenv()

recsPerPage = 5000
label = "PREPSOIL"

def addNS(e):
    if e in ['thumbnailUrl']:
        return SDO[e]
    else:
        return DCTERMS[e]

def urlasid(uri,ds):
    if 'identifier' not in ds or 'doi.org' in uri: # prefer doi
        if uri.startswith('http' and 'doi.org' in uri): # strip doi.org from uri
            pf = uri.split('/')
            del pf[0:2]
            uri = "/".join(pf)
        ds['identifier'] = uri.replace('?','-').replace('#','-').replace('&','-').replace('=','-')

def dict2graph(d):
    g = Graph()
    r = URIRef(d['identifier'])
    for k,v in d.items():
        if isinstance(v, list):
            for i in v:
                g.add((r,addNS(k),Literal(i)))
        else:
            g.add((r,addNS(k),Literal(v)))
    return g

def parseLLLH(r):

    ds = {'relation':[],'subject':[],'type':'project','isReferencedBy':label}
    None

def parseDOC(r):
    # todo; parse subjects as uri's from selected thesauri
    ds = {'relation':[],'subject':[],'type':'document','isReferencedBy':[label]}
    ds['title'] = r.get('title')
    ds['identifier'] = r["field_link_external_resource"].strip()
    if "field_country_select" in r and r["field_country_select"] not in [None,'']:
        ds['subject'] += [c.strip() for c in r["field_country_select"].split(",") if c.strip() != '']  
    if "field_land_type" in r and r["field_land_type"] not in [None,'']:
        ds['subject'] += [c.strip() for c in r["field_land_type"].split(",") if c.strip() != ''] 
    if "field_language" in r and r["field_language"] not in [None,'']:
        ds['language'] = r['field_language']
    if "field_media_format" in r and r["field_media_format"] not in [None,'']:
        ds['format'] = [c.strip() for c in r["field_media_format"].split(",") if c.strip() != ''] 
    if "field_soil_qualities_properties" in r and r["field_soil_qualities_properties"] not in [None,'']:
        ds['subject'] += [c.strip() for c in r["field_soil_qualities_properties"].split(",") if c.strip() != ''] 
    if "field_t_content" in r and r["field_t_content"] not in [None,'']:
        ds['type'] = [c.strip() for c in r["field_t_content"].split(",") if c.strip() != ''] 
    if "field_source" in r and r["field_source"] not in [None,'']:
        ds['isReferencedBy'] += [c.strip() for c in r["field_source"].split(",") if c.strip() != ''] 
    if "field_sustainable_practices" in r and r["field_sustainable_practices"] not in [None,'']:
        ds['subject'] += [c.strip() for c in r["field_sustainable_practices"].split(",") if c.strip() != ''] 
    if "field_soil_mission_objectives" in r and r["field_soil_mission_objectives"] not in [None,'']:
        ds['subject'] += [c.strip() for c in r["field_soil_mission_objectives"].split(",") if c.strip() != '']

    return ds 



# retrieve unparsed records
unparsed = dbQuery(f"select identifier,resultobject,resulttype,title,itemtype from harvest.items where source = '{label}' and (turtle is Null or turtle = '') limit {recsPerPage}")

for rec in sorted(unparsed):
    rid,res,restype,ttl,itemtype = rec
    print(f'Parse {rid}')
    if itemtype == 'lllh': #eudasm
        ds = parseLLLH(json.loads(res))
    else: #document 
        ds = parseDOC(json.loads(res))

    dsRDF = dict2graph(ds)    
    triples = dsRDF.serialize(format='turtle') # todo: strip the namespaces?
    dbQuery(f"update harvest.items set uri=%s, turtle=%s where identifier=%s",(ds['identifier'],triples,rid),False)     




