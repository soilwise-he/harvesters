# import a range of records from a csw endpoint constraint by a filter

from dotenv import load_dotenv
import json
import hashlib
import os
from owslib.iso import *
from owslib.etree import etree
from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsEqualTo, PropertyIsLike, BBox
import sys, uuid
from datetime import datetime
sys.path.append('../utils')
from database import insertRecord

# Load environment variables from .env file
load_dotenv()

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
            identifier=str(uuid.uuid4())
            hierarchy=''
            try:            
                m=MD_Metadata(etree.fromstring(recxml))
                id = m.dataseturi or next(i for i in m.identification[0].uricode if i is not None) or m.identifier
                identifier = m.identifier
                hierarchy = m.hierarchy
            except Exception as e:
                print('Failed parse xml: ', str(e))

            
            insertRecord('harvest.items',['identifier','identifiertype','uri','resultobject','resulttype','hash','source','insert_date','itemtype'],
                         (identifier,'uuid',id,recxml.decode('UTF-8'),'iso19139:2007',hashcode,label,datetime.now(),hierarchy)) # insert into db
            
            # add for duplicate check
            insertRecord('harvest.item_duplicates',['identifier','identifiertype','source','hash'],(identifier,'uuid',label,hashcode))

        except Exception as e:
            print("Parse rec failed;", str(e))




       

               





                