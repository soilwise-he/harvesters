import pycurl
from io import BytesIO
from dotenv import load_dotenv
import json
from pygeometa.schemas.iso19139 import ISO19139OutputSchema
import psycopg2
import hashlib
import os


# Load environment variables from .env file
load_dotenv()

#url= "https://apps.titellus.net/geonetwork/srv/api/search/records/_search"

url = "https://inspire-geoportal.ec.europa.eu/srv/"
reqheaders = ['Content-Type: application/json']

nextRecord = 1
pagesize = 50
maxrecords= 200
total=100
dbconn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT"),
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD")
    )


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
    print('Status: %d' % c.getinfo(c.RESPONSE_CODE))
    print(f'R: {id}, Time: {c.getinfo(c.TOTAL_TIME)}')
    c.close()
    
    response = buffer.getvalue()

    return response

def insertRecord(rec, hashcode, source):

    sql = """INSERT INTO doi.publications(
	identifier, oafresult, uri, insert_date, title, description, subject, creator, publisher, contributor, source, license, hash, type)
	VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    
    with dbconn.cursor() as cur:
        # execute the INSERT statement
        md = rec.get('metadata',{})
        ident = rec.get('identification',{})
        ct = rec.get('contact',{})
        cur.execute(sql, (  md.get('identifier',''), 
                            json.dumps(md), 
                            md.get('dataseturi',''), 
                            md.get('datestamp',''), 
                            ident.get('title',''), 
                            ident.get('abstract',''), 
                            ";".join(ident.get('keywords',{}).get('default',{}).get('keywords',[])), 
                            ct.get('pointOfContact',{}).get('organization',''),
                            ct.get('distributor',{}).get('organization',''),
                            ct.get('contributor',{}).get('organization',''), 
                            source, 
                            ident.get('license',{}).get('url',ident.get('license',{}).get('name','')), 
                            hashcode,
                            md.get('hierarchylevel','') ))
        # commit the changes to the database
        dbconn.commit()
   

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
                    md = ISO19139OutputSchema().import_(r) # import xml to mcf
                    insertRecord(md, hashcode, source='INSPIRE') # insert into db
            except Exception as e:
                print(f'parse-error {id}; {str(e)}')                





                