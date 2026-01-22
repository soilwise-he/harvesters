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
    if e in DCTERMS:
        return DCTERMS[e]
    elif e in SDO:
        return SDO[e]
        

def urlasid(uri,ds):
    if 'identifier' not in ds or 'doi.org' in uri: # prefer doi
        if uri.startswith('http' and 'doi.org' in uri): # strip doi.org from uri
            pf = uri.split('/')
            del pf[0:2]
            uri = "/".join(pf)
        ds['identifier'] = uri.replace('?','-').replace('#','-').replace('&','-').replace('=','-')

def dict2graph(d):
    g = Graph()
    aURI = ''
    if 'identifier' in d and isinstance(d['identifier'], list) and len(d['identifier']) > 0 and d['identifier'][0]:
        for i in d['identifier']:
            if i.startswith('http'):
                aURI = i
    if not aURI.startswith('http'):
        aURI = 'https://soilwise-he.github.io/soil-health#'  + d['identifier'][0]
    r = URIRef(urllib.parse.quote_plus(aURI))
    for k,v in d.items():
        if v and (k in DCTERMS or k in SDO):
            if isinstance(v, list):
                for i in v:
                    g.add((r,addNS(k),Literal(i)))
            else:
                g.add((r,addNS(k),Literal(v)))
    return g


def parseDOC(r):

    # identifier should be []
    if 'identifier' not in r:
        r['identifier'] = []
    elif not isinstance(r['identifier'], list):
        r['identifier'] = [r.get('identifier')] 
    
    if 'id' in r and r['id'] not in [None,''] and r['id'] not in r['identifier']:
        r['identifier'].append(r['id'])
    r.pop('id',None)

    if 'resource' in r and r['resource'] not in [None,''] and r['resource'] not in r['identifier']:
        r['identifier'].append(r['resource'])
    r.pop('resource',None)

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
        desc = next(iter(jsonpath.findall("$.description..", r)), None)
    r['description'] = desc
    ttl = next(iter(jsonpath.findall("$.title.en", r)), None)
    if not ttl:
        ttl = next(iter(jsonpath.findall("$.title..", r)), None)
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
    try:
        trl="/".join(jsonpath.findall("$.temporal[*]..", r))
        if trl:
            r['temporal'] = trl
        else:
            r.pop('temporal',None)
    except:
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

#OTHER FIELDS
# adms_identifier,conforms_to,sample,page,applicable_legislation,hvd_category,version_notes,geocoding_description,spatial_resolution_in_meters
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
    dbQuery(f"update harvest.items set turtle=%s where identifier=%s",(triples,rid),False)     




