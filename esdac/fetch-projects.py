import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys,time,hashlib,os
sys.path.append('utils')
from database import insertRecord, dbQuery

# Load environment variables from .env file
load_dotenv()


startTime = time.perf_counter()
def elapsed():
    return f"{(time.perf_counter() - startTime):0.1f}s"

# for debug, select types to harvest

headers = {'Accept': 'text/html', "User-Agent": "Soilwise Harvest v0.1"}


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

#fetch projects from mission soil
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

       

print("Done")

