





# if record is in english, set language to english?
# else (if not translated by dee yet) keep language


# parse imported html from esdac


from dotenv import load_dotenv
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DC, DCAT, DCTERMS, SKOS, SDO, FOAF
import sys,time,hashlib,os,json,jsonpath
sys.path.append('utils')
from database import insertRecord, dbQuery
import urllib.parse


# Load environment variables from .env file
load_dotenv()

recsPerPage = 5000
label = "DATA.EUROPA.EU"

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
    aURI = d['identifier']
    r = URIRef(urllib.parse.quote_plus(aURI))
    for k,v in d.items():
        if isinstance(v, list):
            for i in v:
                g.add((r,addNS(k),Literal(i)))
        else:
            g.add((r,addNS(k),Literal(v)))
    return g


def parseDOC(r):

    # resource, # or id or identifier
    try:
      r['identifier'] = r['identifier'][0]  
    except:
      None
    
    if 'identifier' not in r or r['identifier'] in [None,''] or not  r['identifier'].startswith('http'):
        r['identifier'] = r['resource'];
    r.pop('resource',None)
    r.pop('id',None)

    r['subject'] = jsonpath.findall("$.subject.resource", r) 
    r['subject'] += jsonpath.findall("$.keywords[*].id", r)
    r.pop('keywords',None)

    hvd = next(iter(jsonpath.findall("$.is_hvd", r)), None)
    if hvd:
        r['subject'] += ['High value dataset']
    r.pop('is_hvd',None)
    r.pop('quality_meas',None)
    r.pop('catalog_record',None)

    country = next(iter(jsonpath.findall("$.country.id", r)), None)
    if country: # if has no spatial, can also use this for spatial
        r['subject'].append(country)
    r.pop('country',None)
    r['subject'] += jsonpath.findall("$.categories.id", r)
    r.pop('categories',None)
    r['language'] = next(iter(jsonpath.findall("$.language[*].id", r)), None)
    desc = next(iter(jsonpath.findall("$.description.en", r)), None)
    if not desc: # then use first lang
        desc = next(iter(jsonpath.findall("$.description.[*]", r)), None)
    r['description'] = desc
    ttl = next(iter(jsonpath.findall("$.title.en", r)), None)
    if not ttl:
        ttl = next(iter(jsonpath.findall("$.title.[*]", r)), None)
    r['title'] = ttl
    cat = next(iter(jsonpath.findall("$.catalog.homepage", r)), None)
    if cat:
        r['isReferencedBy'] = cat
    r.pop('catalog',None)
    r.pop('translation_meta',None)
    r.pop('index',None)
    r['license'] = next(iter(jsonpath.findall("$.distributions[*].license.resource", r)), None)
    r['publisher'] = next(iter(jsonpath.findall("$.publisher.resource", r)), None)
    r['creator'] = jsonpath.findall("$.contact_point[*].name", r)
    r.pop('contact_point',None)
    r['references'] = jsonpath.findall("$.distributions[*].access_url[0]", r)
    r['format'] = list(set(jsonpath.findall("$.distributions[*].format.id", r))) # unique values only
    r.pop('distributions',None)
    r['spatial'] = json.dumps(jsonpath.findall("$.spatial[0].coordinates[*]", r))
    trl="/".join(jsonpath.findall("$.temporal[*].[*]", r))
    if trl:
        r['temporal'] = trl
    else:
        r.pop('temporal',None)
    r['references'] += jsonpath.findall("$.landing_page[*].resource", r) 
    r.pop('landing_page',None)
    rels = jsonpath.findall("$.relation[*].resource", r) 
    if rels:
        r['relation'] = rels
    else:
        r.pop('relation',None)
    accrper = next(iter(jsonpath.findall("$.accrual_periodicity.resource", r)), None)
    if accrper:
        r['accrualPeriodicity'] = accrper
    r.pop('accrual_periodicity',None)
    accrts = next(iter(jsonpath.findall("$.access_right.resource", r)), None)
    if accrts:
        r['accessRights'] = accrper
    r.pop('access_right',None)
    ivo = jsonpath.findall("$.is_version_of[*]", r)
    if ivo:
        r['isVersionOf'] = ivo
    r.pop('is_version_of',None)
    hv = jsonpath.findall("$.version_info", r)
    if hv:
        r['hasVersion'] = hv
    r.pop('version_info',None)


    r.pop('adms_identifier',None)
    r.pop('conforms_to',None)
    r.pop('sample',None)
    r.pop('page',None)
    r.pop('applicable_legislation',None)
    r.pop('hvd_category',None)
    r.pop('version_notes',None)
    r.pop('geocoding_description',None)
    return r 



# retrieve unparsed records
unparsed = dbQuery(f"select identifier,resultobject,resulttype,title,itemtype from harvest.items where source = '{label}' and (turtle is Null or turtle = '')")

print('parse',len(unparsed),'records')

for rec in sorted(unparsed):
    rid,res,restype,ttl,itemtype = rec
    print(f'Parse {rid}')
    ds = parseDOC(json.loads(res))

    dsRDF = dict2graph(ds)    
    triples = dsRDF.serialize(format='turtle') # todo: strip the namespaces?
    dbQuery(f"update harvest.items set uri=%s, turtle=%s where identifier=%s",(ds['identifier'],triples,rid),False)     




