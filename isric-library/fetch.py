import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys,time,hashlib,os
sys.path.append('utils')
from database import insertRecord, dbQuery, hasSource

# Load environment variables from .env file
load_dotenv()

perpage = 100
totalpages = int(10250/perpage)

label = 'ISRIC-LIB'
iurl = 'https://library.wur.nl/WebQuery/isric'

headers = { 'Content-Type': 'text/plain; charset=utf-8' }

# add source if it does not exist
hasSource(label,iurl,'',label)

print('Fetch isric maps')
duplicates = []
for i in range(0,totalpages):
    print(f'{perpage} at {i*perpage} from 1050')
    url = f'{iurl}/start?q=map&wq_flt=documenttype&wq_val=Map&wq_max={perpage}&wq_srt_asc=titel&wq_ofs={i*perpage+1}'
    
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    tbl = soup.find("div", {"id": "search_result"})
    tb = tbl.find("tbody")
    for tr in tb.find_all("tr"): 
        try:
            id = tr.find("a",{"class":"wl_icon wl_magnify"}).get('href','').split('/').pop()
            if id:
                ris = f'{iurl}/isric.ris/{id}'   
                r = requests.get(ris, headers=headers)
                r.encoding = r.apparent_encoding
                txt = r.text
                
                hashcode = hashlib.md5(txt.encode("utf-8")).hexdigest() # get unique hash for html 
                insertRecord(   identifier=id,
                                uri=ris,
                                identifiertype='id',
                                resulttype='citation',
                                resultobject=txt,
                                hashcode=hashcode,
                                source=label,
                                itemtype='Map') # insert into db
        except Exception as e:
            print('error',e)
