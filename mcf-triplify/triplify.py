from dotenv import load_dotenv
from pygeometa.schemas.dcat import DCATOutputSchema
from pygeometa.core import read_mcf
import sys,yaml
from yaml.loader import SafeLoader
sys.path.append('../utils')
from database import dbQuery
from rdflib import Graph

# Load environment variables from .env file
load_dotenv()

# fetch the mcf's

recs = dbQuery("Select hash,oafresult from doi.publications where source = 'INSPIRE'")

for row in recs:
    hashcode = row[0]
    cnf = yaml.load(row[1], Loader=SafeLoader)
    dcat_os = DCATOutputSchema()
    jsonld = dcat_os.write(cnf)
    print(jsonld)

    # convert to ttl
    g = Graph()
    g.parse(data=cnf, format='json-ld')
    foo = g.serialize(format='turtle')

    recs = dbQuery(f"update doi.publications set turtle = '{foo}' where hash = '{hashcode}'")

