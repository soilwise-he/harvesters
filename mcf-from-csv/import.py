import csv, requests, os, yaml, sys, hashlib, json
from dotenv import load_dotenv
from yaml.loader import SafeLoader
from jinja2 import Environment
sys.path.append('utils')
from database import insertRecord, dbQuery, hasSource
load_dotenv()

# import a csv using a template
url = os.environ.get("HARVEST_URL")
if not url:
    print('env HARVEST_URL not set')
    exit
else:
    print('harvest', url)

label = os.environ.get("HARVEST_LABEL").upper() or url
# add source if it does not exist
hasSource(label,url,'',label)

CSV_URL = os.getenv('CSV_URL')
JINJA_URL = os.getenv('JINJA_URL') # or use csv-url with .j2 extension 
sep = os.getenv('CSV_SEP') or ','
enc = os.getenv('CSV_ENC') or 'utf-8'


# set template (first get the file with request)
with open(JINJA_URL) as f1:
    map = f1.read()
env = Environment(extensions=['jinja2_time.TimeExtension'])
j2_template = env.from_string(map)


with open(CSV_URL, newline='', encoding=enc) as csvfile:
    rd = csv.reader(csvfile, delimiter=sep)
    cols=None
    for row in rd:
        if not cols:
            cols = row
        else:
            md = {}
            for i in range(len(cols)):
                if len(row) > i: # some rows shorter then header
                    md[cols[i]] = row[i] or ''
                else:
                    md[cols[i]] = ''
            #Filter remove any None values
            # md = {k:v for k, v in md.items() if pd.notna(v)}
            # for each row, substiture values in a yml
            yMcf = None
            try:    
                mcf = j2_template.render(md=md)
                try:
                    yMcf = yaml.load(mcf, Loader=SafeLoader)
                except Exception as e:
                    print('Failed parsing',mcf,e)
            except Exception as e:
                print('Failed substituting',md,e)    
            
            ttl = md.get('title',{}).get('en','')
            hashcode = hashlib.md5(json.dumps(md).encode("utf-8")).hexdigest() # get unique hash for html 
            insertRecord(
                identifier=id,
                identifiertype='uuid',
                title=ttl,
                resulttype='JSON',
                resultobject=yaml.dump(md),
                hashcode=hashcode,
                source=label,
                itemtype='dataset') # insert into db