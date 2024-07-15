import html5lib
from bs4 import BeautifulSoup
from pyRdfa import pyRdfa
from dotenv import load_dotenv
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DC, DCAT, DCTERMS, SKOS, SDO, FOAF
import sys,time,hashlib,os
sys.path.append('../utils')
from database import insertRecord, dbQuery

# Load environment variables from .env file
load_dotenv()

def fullurl(u):
    if u.startswith('/'):
        u = 'https://esdac.jrc.ec.europa.eu/'+u
    return u

rid="http://example.com/foo"
ttl=""
res='''<div class="views-row views-row-19 views-row-odd">
    
<style>

.t00{
   /*background-color: rgba(247, 247, 247, 1);*/
   border:0px solid silver;
   border-radius:8px;
   padding-top:5px;
   padding-bottom:5px;
   margin-top:5px;
   border-bottom: 1px solid #E8E8E8;

}

.bb{
  font-size: 1.2em;
  height:1.3em;
  vertical-align: top;
  border-bottom: 0px solid #D5E4EB !important;
}

#request_form_button{
 color:white;
 background:orange;
 margin-top:5px;
 padding:3px;
 border-radius:4px;
}

#app_serv_button{
 color:white;
 background:rgb(119, 156, 179);
 margin-top:15px;
 padding:2px;
 border-radius:0px;
}

</style>

<div style="width:98%">

<table class="t00" width="100%">
 <tbody><tr>
	<td width="20%" rowspan="4">
		<center>
			 <img src="https://esdac.jrc.ec.europa.eu/public_path//shared_folder/doc_pub/conservation%20biology.png" width="100" alt="Retaining natural vegetation to safeguard biodiversity and humanity" title="Retaining natural vegetation to safeguard biodiversity and humanity">			 <div style="margin-top:10px;margin-bottom:10px;">
			 <a href="https://doi.org/10.1111/cobi.14040" target="_blank" aria-label="Download" title="Download"><i class="fa fa-download fa-2x"></i></a>			 </div>
		</center>
	</td>
	<td class="bb" colspan="2"><h5>Retaining natural vegetation to safeguard biodiversity and humanity</h5></td>
 </tr>
 <tr>
	<td width="40%" valign="top">
		<b>Resource Type: </b><a href="/resource-type/documents" typeof="skos:Concept" property="rdfs:label skos:prefLabel" datatype="" class="active">Documents</a>, <a href="/resource-type/publications-journals" typeof="skos:Concept" property="rdfs:label skos:prefLabel" datatype="">Publications in Journals</a>, <a href="/DocumentsPublications" typeof="skos:Concept" property="rdfs:label skos:prefLabel" datatype="">Maps &amp; Documents</a> <br>

	</td>
	<td width="40%" valign="top">

												 				 <b>Year: </b><span class="date-display-single" property="dc:date" datatype="xsd:dateTime" content="2023-01-01T00:00:00+01:00">2023</span> <br>				 				 

	</td>
 </tr>
 <tr>

	<td colspan="2">
		<div class="open_att_new_win">
			  			  </div>
	</td>
 </tr>
 <tr>

    <td colspan="2">
		<div class="field-content"><div class="field-expander field-expander-0"><div class="summary" style="display: block;"><p>Global efforts to deliver internationally agreed goals to reduce carbon emissions, halt biodiversity loss, and retain essential ecosystem services have been poorly integrated. These goals rely in part on preserving natural (e.g., native, largely unmodified) and seminatural (e.g., low intensity or sustainable human use) forests, woodlands, and grasslands. To show how to unify these goals, we empirically derived spatially explicit, quantitative, area-based targets for the retention of natural and<span class="read-more" style="display: inline;">...<a href="#" class="more-link">Expand »</a></span></p></div> <div class="details" style="display: none;"><p>Global efforts to deliver internationally agreed goals to reduce carbon emissions, halt biodiversity loss, and retain essential ecosystem services have been poorly integrated. These goals rely in part on preserving natural (e.g., native, largely unmodified) and seminatural (e.g., low intensity or sustainable human use) forests, woodlands, and grasslands. To show how to unify these goals, we empirically derived spatially explicit, quantitative, area-based targets for the retention of natural and seminatural (e.g., native) terrestrial vegetation worldwide. We used a 250-m-resolution map of natural and seminatural vegetation cover and, from this, selected areas identified under different international agreements as being important for achieving global biodiversity, carbon, soil, and water targets. At least 67 million km2 of Earth's terrestrial vegetation (∼79% of the area of vegetation remaining) required retention to contribute to biodiversity, climate, soil, and freshwater conservation objectives under 4 United Nations’ resolutions. This equates to retaining natural and seminatural vegetation across at least 50% of the total terrestrial (excluding Antarctica) surface of Earth. Retention efforts could contribute to multiple goals simultaneously, especially where natural and seminatural vegetation can be managed to achieve cobenefits for biodiversity, carbon storage, and ecosystem service provision. Such management can and should co-occur and be driven by people who live in and rely on places where natural and sustainably managed vegetation remains in situ and must be complemented by restoration and appropriate management of more human-modified environments if global goals are to be realized.</p>
<p><a href="https://doi.org/10.1111/cobi.14040" target="_blank">https://doi.org/10.1111/cobi.14040</a></p><span class="read-less"><a href="#" class="less-link">Collapse</a></span></div></div></div>	</td>
 </tr>

 </tbody></table>

</div>
  </div>'''


s2 = BeautifulSoup(res, 'html.parser')

ds = {'relation':[],'subject':[],'type':'document'}

for i in s2.find_all("img"):
    ds['title'] = i.get('title')
    ds['thumbnailUrl'] = fullurl(i.get('src'))
    break
for l in s2.find_all('a',{'typeof':"skos:Concept"}):
    for kw in l.text.split('; '):
        ds['subject'].append(kw)
for d in s2.find_all("span",{"property":"dc:date"}):
    ds['date'] = d.text
for f in s2.find_all("span",{"class":"file"}):
    for fl in f.find_all("a"):
        ds['relation'].append(fullurl(fl.get('href')))
        ds['identifier'] = fullurl(fl.get('href'))
for desc in s2.find_all("div",{"class":"details"}):
    for desc2 in desc.find_all("p"):
        ds['description'] = desc.text
        break # only first
    for a in desc.find_all("a"):
        ds['identifier'] = fullurl(a.get('href'))
        ds['relation'].append(fullurl(a.get('href')))

print(ds)