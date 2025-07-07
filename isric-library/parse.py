from dotenv import load_dotenv
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
    
    txt2 = txt.splitlines()
    md = {'creator':[],'subject':[],'isReferencedBy':label,'identifier':[uri],'contributor':'ISRIC - World Soil Information'}
    tps = {'AU':'creator','KW':'subject','TY':'type','ID':'identifier','N2':'abstract','AV':'source','PB':'publisher','UR':'references','PY':'date','T1':'title','CY':'source'}
    mdn1 = []
    for l in txt2:
        tp = l[:2]
        if tp.isalnum():
            ln = l[6:]
            if ln.strip() not in [None,'']:
                if tp == 'ID':
                    None
                elif tp in ['AU','KW']:
                    md[tps.get(tp)].append(ln)
                elif tp in ['C1','C2','ER']:
                    mdn1.append(ln)
                elif tp == 'N1':
                    if ':' in ln:
                        k = ln.split(':')[0].strip()
                        v = ln.split(':')[1].strip()
                        if k == 'GeoJSON bbox':
                            md['spatial'] = v
                        elif k == 'Country':
                            None # 2 letter code, full country is also mentioned
                        elif k in ['Library holding','Former ISRIC-id','Link report-map','Map']:
                            md['identifier'].append(v)
                        elif k in ['sndegr','wedegr']:
                            None
                        else:
                            md['subject'].append(v)
                    else:
                        mdn1.append(ln)
                elif tp in tps.keys():
                    md[tps.get(tp,tp)] = ln
                else:
                    md['subject'].append(ln)
    md['abstract'] = md.get('abstract','') + ','.join(mdn1)

    if md['identifier'] == []:
        md['identifier'] = rid

    dsRDF = dict2graph(md)    
    triples = dsRDF.serialize(format='turtle') # todo: strip the namespaces?
    dbQuery(f"update harvest.items set turtle=%s where identifier=%s",(triples,rid),False)
