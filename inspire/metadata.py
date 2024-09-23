import pycurl
from io import BytesIO
from dotenv import load_dotenv
import json, sys
from owslib.iso import *
from owslib.etree import etree
import hashlib
import os,time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
 
# call script from root as ./inpire/metadata.py
 
import sys
 
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
 
from utils.database import insertRecord
# Load environment variables from .env file
load_dotenv()
 
#url= "https://apps.titellus.net/geonetwork/srv/api/search/records/_search"
 
# Constants
URL = "https://inspire-geoportal.ec.europa.eu/srv/"
LABEL = 'INSPIRE'
REQ_HEADERS = ['Content-Type: application/json']
PAGE_SIZE = 50
MAX_RECORDS = 500
 
def get_records(next_record, page_size):
    recsrequest = {
        "from": next_record,
        "size": page_size,
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
                            }#,
                            #{
                            #    "query_string": {
                            #        "query": "(th_httpinspireeceuropaeumetadatacodelistSpatialScope-SpatialScope.link:*national*)"
                            #    }
                            #}
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
    c.setopt(c.URL, URL+"api/search/records/_search")
    c.setopt(c.SSL_VERIFYPEER, 0)
    c.setopt(c.SSL_VERIFYHOST, 0)
    c.setopt(c.POSTFIELDS, json.dumps(recsrequest))
    c.setopt(c.HTTPHEADER, REQ_HEADERS)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
 
    print(f'R: {next_record}, S: {c.getinfo(c.RESPONSE_CODE)}, Time: {c.getinfo(c.TOTAL_TIME)}')
    c.close()
   
    response = buffer.getvalue()
 
    return json.loads(response)
 
def getRecord(id):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, URL+'api/records/'+str(id)+"/formatters/xml?approved=true")
    c.setopt(c.SSL_VERIFYPEER, 0)
    c.setopt(c.SSL_VERIFYHOST, 0)
    c.setopt(c.HTTPHEADER, REQ_HEADERS)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
   
    response = buffer.getvalue()
 
    return response
 
def process_record(rec):
    start_time = time.time()
    try:
        id = rec.get('_source', {}).get('id')
        if id:
            print(f'Fetch record {id}')
            r = getRecord(id)  # get full iso record
            if r and r not in [None, '']:
                hashcode = hashlib.md5(r).hexdigest()  # get unique hash for xml
 
                hierarchy = ''
                identifier = ''
 
                try:
                    m = MD_Metadata(etree.fromstring(r))  # use owslib to parse iso metadata
                    identifier = f"{URL}api/records/{m.identifier}"
 
                    id = m.identifier
                    if m.dataseturi not in [None, ''] and m.dataseturi.startswith('http'):
                        identifier = m.dataseturi
                    elif id not in [None, ''] and id.startswith('http'):
                        identifier = id
                    else:
                        for i in m.identification:
                            for i2 in i.uricode:
                                if i2 not in [None, '']:
                                    identifier = i2
                    if identifier in [None, '']:
                        identifier = id
 
                    hierarchy = m.hierarchy
                except Exception as e:
                    print(f'Failed parse xml for id:{id}, {str(e)}, {str(sys.exc_info())}')
 
                insertRecord(identifier=id,
                             uri=identifier,
                             identifiertype='uuid',
                             resulttype='iso19139:2007',
                             resultobject=r.decode('UTF-8'),
                             hashcode=hashcode,
                             source=LABEL,
                             itemtype=hierarchy)  # insert into db
            else:
                print(f'No record at {id}')
    except Exception as e:
        print(f'parse-error {id}; {str(e)}')
    finally:
        end_time = time.time()
        print(f'Processing time for record {id}: {end_time - start_time:.2f} seconds')
 
def main():
    start_time = datetime.now()
    print(f"Script started at: {start_time}")
 
    next_record = 1
    total = 100
    records_processed = 0
 
    with ThreadPoolExecutor(max_workers=5) as executor:
        while next_record < total and next_record < MAX_RECORDS:
            res = get_records(page_size=PAGE_SIZE, next_record=next_record)
            total = res.get('hits', {}).get('total', {}).get('value', 0)
            next_record += PAGE_SIZE
 
            futures = [executor.submit(process_record, rec) for rec in res.get('hits', {}).get('hits', [])]
            for future in as_completed(futures):
                future.result()  # Will raise exceptions occured
                records_processed += 1
 
    end_time = datetime.now()
    duration = end_time - start_time
 
    print(f"Script completed at: {end_time}")
    print(f"Total runtime: {duration}")
 
if __name__ == "__main__":
    main()