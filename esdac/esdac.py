import requests
from bs4 import BeautifulSoup
from pyRdfa import pyRdfa
from dotenv import load_dotenv

import sys,time,hashlib
sys.path.append('../utils')
from database import insertRecord

# Load environment variables from .env file
load_dotenv()

print('Fetch & parse ESDAC datasets')
url = 'https://esdac.jrc.ec.europa.eu/dataset-list/dataset/28'
label = 'ESDAC'

html = requests.get(url).text
soup = BeautifulSoup(html, 'html.parser')
for tr in soup.find_all('tr'):
    i=0
    md = {}
    for td in tr.find_all('td'):
        if i==1:
            md['title'] = td.text
            md['identifier'] = 'https://esdac.jrc.ec.europa.eu/content/' + td.text.replace(' ','-').replace(':','').replace('(','').replace(')','').lower()
        elif i==2:
            md['abstract'] = td.text
        elif i==3:
            md['year'] = td.text
        i=i+1

    if 'title' in md and md['title'] not in [None,''] and 'identifier' in md and md['identifier'] not in [None,'']:
        try:            
            graph = pyRdfa().graph_from_source(md['identifier'])
            triples = graph.serialize(format='turtle')

            hashcode = hashlib.md5(triples.encode("utf-8")).hexdigest() # get unique hash for xml 
                    
            id = md['identifier']
            identifier = md['identifier']
            hierarchy = 'dataset'

            insertRecord(   identifier=identifier,
                            uri=id,
                            identifiertype='uuid',
                            resulttype='esdac',
                            resultobject=triples,
                            hashcode=hashcode,
                            source=label,
                            itemtype=hierarchy) # insert into db

        except Exception as e:
            print('Error:',md['identifier'],str(e))

