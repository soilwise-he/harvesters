# import a range of records from a csw endpoint constraint by a filter

from dotenv import load_dotenv
import json, sys, hashlib, os, uuid
from owslib.iso import *
from owslib.etree import etree
from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsEqualTo, PropertyIsLike, BBox
from datetime import datetime
sys.path.append('utils')
from database import insertRecord,dbQuery,hasSource

# Load environment variables from .env file
load_dotenv()

url = os.environ.get("HARVEST_URL")
if not url:
    print('env HARVEST_URL not set')
    exit
else:
    print('harvest',url)

label = os.environ.get("HARVEST_LABEL").upper() or url
filters = None
if os.environ.get("HARVEST_FILTER"):
    filterstring = os.environ.get("HARVEST_FILTER")
    print('Filter:', filterstring)
    filters = json.loads(filterstring)

# add source, if it does not exist yet
hasSource(label,url,os.environ.get('HARVEST_FILTER'),'CSW')

nextRecord = 1
pagesize = 50
maxrecords= 2500
matched = 2500

csw = CatalogueServiceWeb(url)

returned = 1
recs = {}

filterMapping = {
    "any": 'csw:AnyText',
    "title": 'dc:title',
    "keyword": 'dc:subject',
    "type": 'dc:type',
    "id": 'dc:identifier'
    }

constraints = []
if filters and len(filters) > 0:
    for f in filters:
        for k,v in f.items():
            key = filterMapping.get(k,k)
            # todo: check if key is in getcapabilities
            if key.lower().split(':').pop() in ["title,description,abstract,anytext"]:
                constraints.append(PropertyIsLike(key, v, matchCase=False))
            else:
                constraints.append(PropertyIsEqualTo(key, v))

while nextRecord > 0 and returned > 0 and nextRecord < matched and nextRecord < maxrecords:
    reqsuc = False
    try:
        if len(constraints) > 0:
            csw.getrecords2(maxrecords=pagesize,outputschema='http://www.isotc211.org/2005/gmd',constraints=constraints,startposition=nextRecord,esn='full')
        else:
            csw.getrecords2(maxrecords=pagesize,outputschema='http://www.isotc211.org/2005/gmd',startposition=nextRecord,esn='full')
        reqsuc = True
    except Exception as e:
        print(f"Request recs failed; {str(e)}")
        nextRecord = nextRecord+pagesize
    
    if reqsuc:  
        print('CSW query ' + str(csw.results['returned']) + ' of ' + str(csw.results['matches']) + ' records from ' + str(nextRecord) + '.')
        matched = csw.results.get('matches',0)
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
    



       

               





                