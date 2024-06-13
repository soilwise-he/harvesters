# import a range of records from a csw endpoint constraint by a filter

from dotenv import load_dotenv
import json
import hashlib
import os
from owslib.iso import *
from owslib.etree import etree
from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsEqualTo, PropertyIsLike, BBox
import sys,time
sys.path.append('../utils')
from database import insertRecord

# Load environment variables from .env file
load_dotenv()

#url= "https://apps.titellus.net/geonetwork/srv/api/search/records/_search"

url = os.environ.get("HARVEST_URL")
if not url:
    print('env HARVEST_URL not set')
    exit
label = os.environ.get("HARVEST_LABEL") or url
filters = None
if os.environ.get("HARVEST_FILTER"):
    filters = json.loads(os.environ.get("HARVEST_FILTER"))

reqheaders = ['Content-Type: application/json']

nextRecord = 1
pagesize = 50
maxrecords= 2500

csw = CatalogueServiceWeb(url)

# qry = PropertyIsEqualTo('csw:AnyText', 'soil')

returned = 1
recs = {}

filterMapping = {
    "any": 'csw:AnyText',
    "title": 'dc:title',
    "keyword": 'dc:subject',
    "type": 'dc:type'
    }

constraints = []
if filters and len(filters.keys()) > 0:
    for f in filters:
        key = filterMapping.get(f,f)
        # todo: check if key is in getcapabilities
        constraints.append(PropertyIsEqualTo(key, filters[f]))

while nextRecord > 0 and returned > 0 and nextRecord < maxrecords:
    csw.getrecords2(maxrecords=pagesize,outputschema='http://www.isotc211.org/2005/gmd',startposition=nextRecord,esn='full')
    print('CSW query ' + str(csw.results['returned']) + ' of ' + str(csw.results['matches']) + ' records from ' + str(nextRecord) + '.')
    nextRecord = csw.results['nextrecord'] or (nextRecord+pagesize)
    returned = csw.results['returned'] or len(csw.records)
    
    for rec in csw.records:
        recxml = csw.records[rec].xml
        try:
            if 'GetRecordByIdResponse' in str(recxml):
                try:
                    doc = etree.fromstring(recxml)
                except ValueError:
                    print(f'iso19139 parse failed {u}')
                    doc = etree.fromstring(bytes(recxml, 'utf-8'))
                nsmap = {}
                for ns in doc.xpath('//namespace::*'):
                    if ns[0]:
                        nsmap[ns[0]] = ns[1]

                rec2 = doc.xpath('gmd:MD_Metadata', namespaces=nsmap)
                recxml = etree.tostring(rec2[0])

            hashcode = hashlib.md5(recxml).hexdigest() # get unique hash for xml 

            id=''
            hierarchy=''
            try:            
                m=MD_Metadata(etree.fromstring(recxml))
                id = m.dataseturi or next(i for i in m.identification[0].uricode if i is not None) or m.identifier
                hierarchy = m.hierarchy
            except Exception as e:
                print(e)

            #md = ISO19139OutputSchema().import_(recxml) # import xml to mcf
            insertRecord('doi.publications',['identifier','uri','oafresult','hash','source','type','insert_date'],
                         (m.identifier,id,recxml.decode('UTF-8'),hashcode,label,hierarchy,time.time())) # insert into db

        except Exception as e:
            print(f"Parse rec failed ; {str(e)}")




       

               





                