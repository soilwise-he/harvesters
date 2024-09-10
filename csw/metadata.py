# import a range of records from a csw endpoint constraint by a filter

from dotenv import load_dotenv
import json, sys, hashlib, os, uuid
from owslib.iso import *
from owslib.etree import etree
from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsEqualTo, PropertyIsLike, BBox
from datetime import datetime
sys.path.append('utils')
from database import insertRecord,dbQuery

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

# check if source is in sources table
sources = dbQuery(f"select from harvest.sources where name is upper({label})")
if not sources:
    dbQuery(f"insert into harvest.sources set name,url,filter,type values '{label}','{url}','{filters}','CSW' ",False)
    
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
                id = m.dataseturi
                if id in [None,'']:
                    for i in m.identification:
                        for i2 in i.uricode:
                            if i2 not in [None,'']:
                                id = i2
                if id in [None,'']:
                    id = m.identifier
                identifier = m.identifier
                hierarchy = m.hierarchy
            except Exception as e:
                print(f'Failed parse xml: {str(e)} {str(sys.exc_info())}')

            insertRecord(       identifier=id,
                                uri=identifier,
                                identifiertype='uuid',
                                resulttype='iso19139:2007',
                                resultobject=recxml.decode('UTF-8'),
                                hashcode=hashcode,
                                source=label,
                                itemtype=hierarchy) # insert into db
            
        except Exception as e:
            print(f"Parse rec failed; {str(e)}")




       

               





                