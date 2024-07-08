
from pycsw.core import config as pconfig
from pycsw.core import metadata, repository, util
from pycsw.core.etree import etree
from pycsw.core.etree import PARSER
from pycsw.core.util import parse_ini_config
from rdflib import Graph
import traceback

import json, os, psycopg2

import sys
sys.path.append('../utils')
from database import dbQuery

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# todo: dublin core parser for json, maybe even use rdflib, ask tom

context = pconfig.StaticContext()
force_update = os.environ.get('force_update') or False

database = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}" 

table = os.environ.get('PYCSW_TABLE') or 'records'

repo = repository.Repository(database, context, table=table)

# get records to be imported from db (updated after xxx?) or "where id not in (select id from records)"
# if failed, save as failed, not ask again, or maybe later
recs = dbQuery(f"select DISTINCT ON (identifier) identifier, resultobject from harvest.items where identifier is not null and identifier not in (select identifier from {table}) limit 100")
loaded_files = []

if recs:
    total = len(recs)
    counter = 0
    
    for rec in sorted(recs):
        id, recfile = rec
        counter += 1
        metadata_record = None

        print(f'Processing record {id} ({counter} of {total})')

        if recfile not in [None,'']:

            # read document
            try:
                metadata_record = json.loads(recfile)
                metadata_record['@context'] = "https://www.w3.org/ns/dcat.jsonld"
                metadata_record['@id'] = id

                print(f'parse {id} as json, try ld')
                try:
                    g = Graph()
                    g.parse(data=json.dumps(metadata_record), format='json-ld')
                    metadata_record = etree.fromstring(bytes(g.serialize(format="xml"), 'utf-8'))
                    print(f'parse {id} as json-ld, {metadata_record}')
                except Exception as err:
                    print(f'failed parse as json-ld, {err} {traceback.print_stack()}')

            except json.decoder.JSONDecodeError as err:
                print(f'{id} no json -> xml')
            except Exception as err:
                print(f'failed parse as json, try xml; {err}')
            
            if metadata_record in [None,'']:
                try:
                    metadata_record = etree.fromstring(recfile)
                    print(f'parse {id} as xml')
                except etree.XMLSyntaxError as err:
                    print(f'XML document {id} is not well-formed {err}')
                except Exception as err:
                    print(f'XML document {id} is not string, {err}')
                    metadata_record = etree.fromstring(bytes(recfile, 'utf-8'))

            if metadata_record in [None,'']:
                

                try:
                    g = Graph()
                    g.parse(data=recfile)
                    metadata_record = etree.fromstring(g.serialize(format="xml"))
                    print(f'parse {id} as rdf')
                except Exception as err:
                    print(f'failed parse as rdf, stop trying; {err}')
            try:
                record = metadata.parse_record(context, metadata_record, repo)
            except Exception as err:
                print(f'Could not parse {id} as record, {err}, {traceback.print_exc()}')
                continue

            for rec in record:
                print(f'Inserting {rec.typename} {rec.identifier}')

                try:
                    repo.insert(rec, 'local', util.get_today_and_now())
                    loaded_files.append(id)
                    print(f'Inserted {id}')
                except Exception as err:
                    if force_update:
                        print(f'Record {id} exists. Updating.')
                        repo.update(rec)
                        print(f'Updated {id}')
                        loaded_files.append(id)
                    else:
                        print(f'ERROR: {id} not inserted: {err}')

                    #in some cases the origianl id is not the derived id, update it
                    if '' not in [id,rec.identifier] and id != rec.identifier:
                        print(f'updating asynchronous id {id}')
                        dbQuery(f"update {table} set identifier = '{rec.identifier}' where identifier = '{id}'",(),False)
