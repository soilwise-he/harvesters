import html5lib
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DC, DCAT, DCTERMS, SKOS, SDO, FOAF
import sys,time,hashlib,os
sys.path.append('../utils')
from database import insertRecord, dbQuery

def fullurl(u):
    if u.startswith('/'):
        u = 'https://esdac.jrc.ec.europa.eu/'+u
    return u

def addNS(e):
    if e in ['thumbnailUrl']:
        return SDO[e]
    else:
        return DCTERMS[e]

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

# Load environment variables from .env file
load_dotenv()

rid="http://example.com/foo"
ttl=""
res=''' <div class="views-row views-row-13 views-row-odd">

<div style="width:98%">
<table class="t00" width="100%">
<tr>
<td rowspan="4" width="20%">
<center>
<img alt="Sâo Luîs/Fortaleza. Mapa de Aptidâo Agrícola. Folha SA.23/24. Volume 3." height="100px" src="/images/Eudasm/latinamerica/images/maps/download/ico/br12012_2.jpg" style="max-width:200px; box-shadow: 5px 5px 5px silver;" title="Sâo Luîs/Fortaleza. Mapa de Aptidâo Agrícola. Folha SA.23/24. Volume 3."/> <div style="margin-top:10px;margin-bottom:10px;">
<a href="/images/Eudasm/latinamerica/images/maps/download/PDF/br12012_2.pdf" target="_blank" title="PDF"><i class="fa fa-file-pdf-o fa-2x"></i></a>
<a href="/images/Eudasm/latinamerica/images/maps/download/br12012_2.jpg" target="_blank" title="File"><i class="fa fa-file-image-o fa-2x"></i></a> </div>
</center>
</td>
<td class="bb" colspan="2" style="padding-left:10px;"><h5>Sâo Luîs/Fortaleza. Mapa de Aptidâo Agrícola. Folha SA.23/24. Volume 3.</h5></td>
</tr>
<tr>
<td style="padding-left:10px;" valign="top" width="40%">
<b>Resource Type: </b><a class="active" datatype="" href="/resource-type/national-soil-maps-eudasm" property="rdfs:label skos:prefLabel" typeof="skos:Concept">National Soil Maps (EUDASM)</a>, <a datatype="" href="/resource-type/maps" property="rdfs:label skos:prefLabel" typeof="skos:Concept">Maps</a>, <a datatype="" href="/DocumentsPublications" property="rdfs:label skos:prefLabel" typeof="skos:Concept">Maps &amp; Documents</a> <br/>
</td>
<td valign="top" width="40%">
<b>Continent: </b><a datatype="" href="/continent/south-america" property="rdfs:label skos:prefLabel" typeof="skos:Concept">South America</a> <br/> <b>Country: </b><img alt="BR" src="/images/flag/png/BR.png" title="BR"/> <span class="country">Brazil</span> <br/> <b>Author: </b>Mapa Realizado Pelo DNPM Para o Programma de intergraçâo Nacional. <br/> <b>Year: </b><span class="date-display-single" content="1973-01-01T00:00:00+01:00" datatype="xsd:dateTime" property="dc:date">1973</span> <br/> <b>Publisher: </b>Departamento Nacional da Produçao Mineral, Rio de Janeiro. <br/> </td>
</tr>
<tr>
<td colspan="2">
<div class="open_att_new_win">
</div>
</td>
</tr>
<tr>
<td colspan="2">
</td>
</tr>
</table>
</div>
</div>

    '''

s2 = BeautifulSoup(res, 'html.parser')

ds = {'relation':[],'subject':[],'type':'dataset'}

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
for p in s2.find_all("a",{"title":"PDF"}):
    ds['relation'].append(fullurl(p.get('href')))

for t in s2.find_all("td",{"valign":"top"}):
    for b in str(t).split('<b>'):
        if b.split('</b>')[0].strip() == 'Publisher:':
            ds['publisher'] = b.split('</b>')[1].split('<br/>')[0]
        elif b.split('</b>')[0].strip() == 'Author:':
            ds['creator'] = b.split('</b>')[1].split('<br/>')[0]

print(ds)
if not 'identifier' in ds or ds['identifier'] in [None,""]:
        ds['identifier'] = rid
dsRDF = dict2graph(ds)    
triples = dsRDF.serialize(format='turtle') 
print('tr',triples)