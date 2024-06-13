import requests
from bs4 import BeautifulSoup
from rdflib import Graph
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
j=0
for tr in soup.find_all('tr'):
    j=j+1
    if j==5:
        exit
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

    if 'title' in md and md['title'] not in [None,'']:
        print('parse', md['identifier'])
        try:            
            graph = pyRdfa().graph_from_source(md['identifier'])
            triples = graph.serialize(format='turtle')

            hashcode = hashlib.md5(triples.encode("utf-8")).hexdigest() # get unique hash for xml 
                    
            id = md['identifier']
            identifier = md['identifier']
            hierarchy = 'dataset'

            insertRecord('doi.publications',['identifier','uri','oafresult','hash','source','type','insert_date'],
                            (identifier,id,triples,hashcode,label,hierarchy,time.time())) # insert into db
        except Exception as e:
            print('Error:',md['identifier'],str(e))

