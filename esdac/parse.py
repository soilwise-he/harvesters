# parse imported html from esdac

from bs4 import BeautifulSoup

from dotenv import load_dotenv
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DC, DCAT, DCTERMS, SKOS, SDO, FOAF
import sys,time,hashlib,os
sys.path.append('utils')
from database import insertRecord, dbQuery

# Load environment variables from .env file
load_dotenv()

recsPerPage = 10000

def fullurl(u):
    if not u.startswith('http'):
        if u.startswith('/'):
            u = 'https://esdac.jrc.ec.europa.eu'+u
        else:    
            u = 'https://esdac.jrc.ec.europa.eu/'+u
    return u

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

def parseEUDASM(s2):
    ds = {'relation':[],'subject':[],'type':'dataset','isReferencedBy':'EUDASM'}
    for i in s2.find_all("img"):
        ds['title'] = i.get('title')
        ds['thumbnailUrl'] = fullurl(i.get('src'))
        break
    for l in s2.find_all('a',{'typeof':"skos:Concept"}):
        for kw in l.text.split('; '):
            ds['subject'].append(kw)
    for d in s2.find_all("span",{"property":"dc:date"}):
        ds['date'] = d.text
    for s in s2.find_all("section",{'id':'block-system-main'}):
        section = s.text
    for l in s2.find_all("span",{"class":"country"}):
        ds['subject'].append(l.text)
    for f in s2.find_all("a",{"title":"File"}):
        ds['relation'].append(fullurl(f.get('href')))
        ds['identifier'] = fullurl(f.get('href')) #set the id to ds url
    for p in s2.find_all("a",{"title":"PDF"}):
        ds['relation'].append(fullurl(p.get('href')))
    for t in s2.find_all("td",{"valign":"top"}):
        for b in str(t).split('<b>'):
            if b.split('</b>')[0].strip() == 'Publisher:':
                ds['publisher'] = b.split('</b>')[1].split('<br/>')[0]
            elif b.split('</b>')[0].strip() == 'Author:':
                ds['creator'] = b.split('</b>')[1].split('<br/>')[0]
    return ds

def parseDOC(s2):
    ds = {'relation':[],'subject':[],'type':'document','isReferencedBy':'ESDAC'}
    for i in s2.find_all("img"):
        ds['title'] = i.get('title')
        ds['thumbnailUrl'] = fullurl(i.get('src'))
        break
    for l in s2.find_all('a',{'typeof':"skos:Concept"}):
        for kw in l.text.split('; '):
            ds['subject'].append(kw)
    for d in s2.find_all("span",{"property":"dc:date"}):
        ds['date'] = d.text
    for f in s2.find_all("a",{"aria-label":"Download"}):
        ds['relation'].append(fullurl(f.get('href')))
        urlasid(f.get('href'),ds)
    for f in s2.find_all("span",{"class":"file"}):
        for fl in f.find_all("a"):
            ds['relation'].append(fullurl(fl.get('href')))
            urlasid(fl.get('href'),ds)
    for desc in s2.find_all("div",{"class":"details"}):
        for desc2 in desc.find_all("p"):
            ds['description'] = desc.text
            break # only first
        for a in desc.find_all("a"):
            urlasid(a.get('href'),ds)
            ds['relation'].append(fullurl(a.get('href')))
    if 'description' not in ds or ds['description'] in [None,'']:
        for desc in s2.find_all("div",{"class":"field-content"}):
            ds['description'] = desc.text
            break
    return ds 

def parseESDAC(s2):
    ds = {'relation':[],'subject':[],'source':[],'type':'dataset','title':ttl,'isReferencedBy':'ESDAC'}
    for desc in s2.find_all('div',{'property':"dct:description"}):
        ds['description'] = desc.text
    for img in s2.find_all('img',{'typeof':"foaf:Image"}):
        if not 'image_captcha' in img.get('src'):
            ds['thumbnailUrl'] = fullurl(img.get('src'))
    for uc in s2.find_all("div",{"class":"field-name-field-data-dataset-notification"}):
        ds['accessRights'] = uc.text
    for ref in s2.find_all("div",{"class":"field-name-field-data-dataset-references"}):
        for ref2 in ref.find_all("li"):
            ds['source'].append(ref2.text)
    for l in s2.find_all('a',{'typeof':"skos:Concept"}):
        for kw in l.text.split('; '):
            ds['subject'].append(kw)
    for dt in s2.find_all("div",{"class":"field-name-field-data-publication-year"}):
        for d in dt.find_all("div",{"class":"field-item"}):
            ds['date'] = d.text
    for ct in s2.find_all("div",{"class":"field-name-field-data-publisher"}):
        for c in ct.find_all("div",{"class":"field-item"}):
            ds['publisher'] = c.text
    return ds

# retrieve unparsed records
unparsed = dbQuery(f"select identifier,resultobject,resulttype,title,itemtype from harvest.items where source = 'ESDAC' and (turtle is Null or turtle = '') limit {recsPerPage}")

for rec in sorted(unparsed):
    rid,res,restype,ttl,itemtype = rec
    print(f'Parse {rid}')
    s2 = BeautifulSoup(res, 'html.parser')
    if res.startswith('<div'): #eudasm or document
        if itemtype == 'dataset': #eudasm
            ds = parseEUDASM(s2)
        else: #document 
            ds = parseDOC(s2)
            None
    else: # full dataset page
        ds = parseESDAC(s2)
    if not 'identifier' in ds or ds['identifier'] in [None,""]:
        ds['identifier'] = rid
    dsRDF = dict2graph(ds)    
    triples = dsRDF.serialize(format='turtle') # todo: strip the namespaces?
    dbQuery(f"update harvest.items set uri=%s, turtle=%s where identifier=%s",(ds['identifier'],triples,rid),False)     




