import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys,time,hashlib,os
sys.path.append('utils')
from database import insertRecord, dbQuery
import urllib.parse
from SPARQLWrapper import SPARQLWrapper, JSON

# Load environment variables from .env file
load_dotenv()

# def ProjectByGrantID (id):
#    url = f'http://api.openaire.eu/search/projects?format=json&grantID={id.split('/').pop()}'
#    prjs = requests.get(url,headers=headers).json
#    prj = prjs['response']['results']['result'][0]['metadata']['oaf:entity']['oaf:project']
#    prj2 = {}
#    prj2['doi'] = prj.get('pid',{}).get('$','')
#    prj2['rcn'] = prj.get('pid',{}).get('$','')
#    prj2['title'] = prj.get('title',{}).get('$','')
#    prj2['desc'] = prj.get('summary',{}).get('$','')
#    prj2['call'] = prj.get('callidentifier',{}).get('$','')
#    prj2['code'] = prj.get('acronym',{}).get('$','')
#    return prj2



headers = {"User-Agent": "Soilwise Harvest v0.1"}

# remove existing
dbQuery('truncate harvest.projects',(),False)

# fetch projects from esdac
print('Fetch ESDAC projects')
url = f'https://esdac.jrc.ec.europa.eu/projects/Eufunded/Eufunded.html'
html = requests.get(url,headers=headers).text
soup = BeautifulSoup(html, "html.parser")
for tbl in soup.find_all("div", {"class": "pane-content"}):
    first = True
    for tr in tbl.find_all("tr"):
        if first:
            first = False
        else:
            r = {}
            td = tr.find_all("td")
            r['abbr'] = td[0].text
            r['name'] = td[1].text
            r['desc'] = td[2].text
            r['link'] = td[3].find('a').get('href')
            
            dbQuery('insert into harvest.projects (code, title, abstract, url) values (%s, %s, %s, %s)', 
                    (r['abbr'],r['name'],r['desc'],r['link']), False)

# fetch projects from mission soil
print('Fetch Mission soil projects')
url = 'https://mission-soil-platform.ec.europa.eu/project-hub/funded-projects-under-mission-soil'
html = requests.get(url,headers=headers).text
soup = BeautifulSoup(html, "html.parser")
for tbl in soup.find_all("table", {"class": "ecl-table"}):
    first = True
    for tr in tbl.find_all("tr"):
        if first:
            first = False
        else:
            r = {}
            td = tr.find_all("td")
            fund = td[0].text
            txt = td[2].text
            lnks = td[2]
            t = 'foo'
            lks={}
            for lnk in lnks.find_all("a"):
                if lnk.previousSibling.text.strip() not in ['',',']:
                    t = lnk.previousSibling
                    lks[t.replace('(','').strip()] = {}
                lks[t.replace('(','').strip()][lnk.text] = lnk.get('href') 

            for k2,v2 in lks.items():                
                dbQuery('insert into harvest.projects (code, funding, website, url ) values (%s, %s, %s, %s)', 
                        ( k2, fund, v2.get('project website',''), v2.get('CORDIS','') ), False)


# get rcn's
recs = dbQuery("select code,url from harvest.projects where rcn is null",(),True)
ids = []
for rec in sorted(recs):
    code,cordisuri = rec
    ids.append(cordisuri.split('/').pop())

if len(ids) > 0: 
    qry = f'''PREFIX eurio:<http://data.europa.eu/s66#>
SELECT DISTINCT ?id ?rcn
WHERE
{{
?project a eurio:Project .
optional {{ ?project eurio:rcn ?rcn . }}
?project eurio:identifier ?id . 
FILTER ( STR(?id) IN ("{'","'.join(ids)}") )
}}'''
    print(qry)
    sparql = SPARQLWrapper("https://cordis.europa.eu/datalab/sparql")
    sparql.setQuery(qry)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(f'Count: {len(results.get("results",{}).get("bindings",[]))}')
    for b in results.get("results",{}).get("bindings",[]):
        if b.get('rcn',{}).get('value') not in [None,'']:
            rcn = b.get('rcn',{}).get('value')
            id2 = b.get('id',{}).get('value') 
            recs = dbQuery("update harvest.projects set rcn = %s where url = %s",(rcn,f'https://cordis.europa.eu/project/id/{id2}'),False)

print("Done")

