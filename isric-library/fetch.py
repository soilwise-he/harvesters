import requests, json
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys,time,hashlib,os
sys.path.append('utils')
from database import insertRecord, dbQuery, hasSource

# Load environment variables from .env file
load_dotenv()

perpage = 50
totalpages = int(10250/perpage)

label = 'ISRIC-LIB'
iurl = 'https://library.wur.nl/WebQuery/isric'

headers = { 'Content-Type': 'text/plain; charset=utf-8' }

# add source if it does not exist
hasSource(label,iurl,'',label)

print('Fetch isric maps')
duplicates = []
for i in range(0,totalpages):
    print(f'{perpage} at {i*perpage} from ')
    url = f'{iurl}/isric.ris?q=map&wq_flt=documenttype&wq_val=Map&wq_max={perpage}&wq_srt_asc=titel&wq_ofs={i*perpage+1}'
    
    txt = requests.get(url).text
    recs = txt.split('\n\n\n')
    for r in recs:
        txt2 = r.splitlines()
        md = {'creator':[],'subject':[],'isReferencedBy':label,'identifier':[],'publisher':'ISRIC - World Soil Information'}
        tps = {'AU':'creator','KW':'subject','TY':'type','ID':'identifier','N2':'abstract','AV':'source','PB':'publisher','UR':'references','Link report-map':'references','PY':'date','T1':'title','CY':'source'}
        mdn1 = []
        for l in txt2:
            tp = l[:2]
            if tp.isalnum():
                ln = l[6:]
                if ln.strip() not in [None,'']:
                    if tp in ['AU','KW','ID','UR']: # list types
                        md.setdefault(tps.get(tp),[]).append(ln)
                        if tp=='UR':
                            print('NOW',ln)
                    elif tp in ['C1','C2','ER']:
                        mdn1.append(ln)
                    elif tp == 'N1':
                        if ':' in ln:
                            k = ln.split(':')[0].strip()
                            v = ln.split(':')[1].strip()
                            if k == 'GeoJSON bbox':
                                md['spatial'] = v
                            elif k == 'Country':
                                None # 2 letter code, full country is also mentioned
                            elif k in ['Library holding','Former ISRIC-id','Map']:
                                md.setdefault('identifier',[]).append(v)
                            elif k in ['Link report-map']:
                                md.setdefault('references',[]).append(f'https://library.wur.nl/WebQuery/isric?monografie/annotatie=={urllib.parse.quote(ln)}')
                            elif k in ['sndegr','wedegr']:
                                None
                            else:
                                md['subject'].append(v)
                        else:
                            mdn1.append(ln)
                    elif tp in tps.keys():
                        md[tps.get(tp,tp)] = ln
                    else:
                        md.setdefault('subject',[]).append(ln)  
        try: 
            ids = md.get("identifier",[])
            anid = None
            if len(ids) > 0:
                anid = ids[0]
                print(ids)          
                ris = f'{iurl}/isric.ris/{anid}'
                md.setdefault('references',[]).append(f'{iurl}/start/{anid}')
                hashcode = hashlib.md5(json.dumps(md).encode("utf-8")).hexdigest() # get unique hash for html 
                insertRecord(   identifier="isn:"+anid,
                            uri=f'{iurl}/start/{anid}',
                            identifiertype='id',
                            resulttype='citation',
                            resultobject=json.dumps(md),
                            hashcode=hashcode,
                            source=label,
                            itemtype='Map') # insert into db
        except Exception as e:
            print('Failed rec',i*perpage,e)
