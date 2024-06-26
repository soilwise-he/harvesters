import pycurl
from io import BytesIO
from dotenv import load_dotenv
import json, sys
from owslib.iso import *
from owslib.etree import etree
import hashlib
import os,time

import sys
sys.path.append('../utils')
from database import insertRecord

# Load environment variables from .env file
load_dotenv()

#url= "https://apps.titellus.net/geonetwork/srv/api/search/records/_search"

url = "https://inspire-geoportal.ec.europa.eu/srv/"
label='INSPIRE'
reqheaders = ['Content-Type: application/json']

nextRecord = 1
pagesize = 50
maxrecords= 500
total=100

def getRecords(nextRecord,pagesize):

    recsrequest = {
        "from": nextRecord,
        "size": pagesize,
        "sort": [
            {"resourceTitleObject.default.sort":"asc"}
        ],
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "terms": {
                                    "isTemplate": [
                                        "n"
                                    ]
                                }
                            },
                            {
                                "query_string": {
                                    "query": '(th_httpinspireeceuropaeutheme-theme.link:"http://inspire.ec.europa.eu/theme/so")'
                                }
                            },
                            {
                                "query_string": {
                                    "query": "(th_httpinspireeceuropaeumetadatacodelistSpatialScope-SpatialScope.link:*national*)"
                                }
                            }
                        ]
                    }
                }
            }
        },
        "_source": {
            "includes": [
                "uuid",
                "id",
                "groupOwnerName",
                "resourceTitleObject"
            ]
        },
        "track_total_hits": True
    }

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url+"api/search/records/_search")
    c.setopt(c.SSL_VERIFYPEER, 0)
    c.setopt(c.SSL_VERIFYHOST, 0)
    c.setopt(c.POSTFIELDS, json.dumps(recsrequest))
    c.setopt(c.HTTPHEADER, reqheaders)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()

    print(f'R: {nextRecord}, S: {c.getinfo(c.RESPONSE_CODE)}, Time: {c.getinfo(c.TOTAL_TIME)}')
    c.close()
    
    response = buffer.getvalue()

    return json.loads(response)

def getRecord(id):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url+'api/records/'+str(id)+"/formatters/xml?approved=true")
    c.setopt(c.SSL_VERIFYPEER, 0)
    c.setopt(c.SSL_VERIFYHOST, 0)
    c.setopt(c.HTTPHEADER, reqheaders)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    
    response = buffer.getvalue()

    return response

while nextRecord < total and nextRecord < maxrecords:

        res = getRecords(pagesize=pagesize,nextRecord=nextRecord)

        total = res.get('hits',{}).get('total',{}).get('value',0)
        nextRecord = nextRecord + pagesize
                
        for rec in res.get('hits',{}).get('hits',[]):
            try: 
                id = rec.get('_source',{}).get('id')
                if id:
                    r = getRecord(id) # get full iso record
                    hashcode = hashlib.md5(r).hexdigest() # get unique hash for xml 
                    
                    hierarchy=''
                    identifier=''

                    try:            
                        m=MD_Metadata(etree.fromstring(r)) # use owslib to parse iso metadata
                        identifier = f"{url}api/records/{m.identifier}"
                        
                        id = m.identifier
                        if m.dataseturi not in [None,''] and m.dataseturi.startswith('http'):
                            identifier = m.dataseturi
                        elif id not in [None,''] and id.startswith('http'):
                            identifier = id
                        else:
                            for i in m.identification:
                                for i2 in i.uricode:
                                    if i2 not in [None,'']:
                                        identifier = i2
                        if identifier in [None,'']:
                            identifier = id

                        hierarchy = m.hierarchy
                    except Exception as e:
                        print(f'Failed parse xml for id:{id}, {str(e)},  {str(sys.exc_info())}')

                    #md = ISO19139OutputSchema().import_(r) # import xml to mcf
                    insertRecord(   identifier=id,
                                    uri=identifier,
                                    identifiertype='uuid',
                                    resulttype='iso19139:2007',
                                    resultobject=r.decode('UTF-8'),
                                    hashcode=hashcode,
                                    source=label,
                                    itemtype=hierarchy) # insert into db

            except Exception as e:
                print(f'parse-error {id}; {str(e)}')                





                