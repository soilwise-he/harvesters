import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys,time,hashlib,os
sys.path.append('utils')
from database import insertRecord, dbQuery

# Load environment variables from .env file
load_dotenv()

# CREATE TABLE IF NOT EXISTS harvest.projects
# (
#     code character varying(99) NOT NULL,
#     title text,
#     funding character varying(99) ,
#     website character varying(99) ,
#     grantnr character varying(99) NOT NULL,
#     source character varying(99) ,
# );
# create unique index idx_hrv_prj_grant_code on harvest.projects (code, grantnr);

print('This harvester ingests projects from esdac and soil mission platform into the harvest.projects table')

startTime = time.perf_counter()
def elapsed():
    return f"{(time.perf_counter() - startTime):0.1f}s"

# for debug, select types to harvest

headers = {'Accept': 'text/html', "User-Agent": "Soilwise Harvest v0.1"}

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
            r['grantnr'] = td[3].find('a').get('href').split('/').pop()
            
            dbQuery("""
            INSERT INTO harvest.projects
            (code, title, grantnr, source)
            VALUES (%s,%s,%s,'esdac')
            ON CONFLICT (grantnr, code)
            DO UPDATE SET
                title = EXCLUDED.title
            """, (r['abbr'],r['name'],r['grantnr']), False)

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
                grantnr = v2.get('CORDIS','').split('/').pop()
                if k2 not in [None,''] and grantnr.isnumeric():                 
                    dbQuery(
                        """insert into harvest.projects (code, funding, website, grantnr, source ) 
                        values (%s, %s, %s, %s, 'Mission soil')
                        ON CONFLICT (grantnr, code)
                        DO UPDATE SET
                        website = EXCLUDED.website,
                        funding = EXCLUDED.funding""", 
                            ( k2, fund, v2.get('project website',''), grantnr ), False)
                else:
                    print(f'{k2} or {grantnr} empty')

    
print("Done")