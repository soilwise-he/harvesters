
from pycsw.core import config as pconfig
from pycsw.core import metadata, repository, util
from pycsw.core.etree import etree
from pycsw.core.etree import PARSER
from pycsw.core.util import parse_ini_config
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DC, DCTERMS, RDF, FOAF, SKOS

import traceback,urllib

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
recs = dbQuery("""select DISTINCT ON (i.identifier) i.identifier, i.title, i.date, s.turtle_prefix, s.type, i.resultobject, i.turtle 
                from harvest.items i, harvest.sources s 
                where i.identifier is not null 
                and i.source = s.name 
                and not exists (
					select identifier from public.records
					where identifier = i.identifier 
                    or identifier like '%%'||i.identifier) 
                order by i.identifier, i.insert_date desc limit 5000""")
loaded_files = []

if recs:
    total = len(recs)
    counter = 0
    
    print('boo')

    for rec in sorted(recs):
        id, title, date, turtle_prefix, rtype, resultobject, turtle  = rec

        if rtype=='SPARQL' and turtle not in [None,'']:
            recfile = f"{turtle_prefix}\r\n{turtle}"
        else:
            recfile = resultobject

        counter += 1
        metadata_record = None

        print(f'Processing record {id} ({counter} of {total})')

        if recfile not in [None,'']:

            if rtype=='SPARQL':
                try:
                    g = Graph()
                    g.parse(data=recfile, format='turtle')

                    if id.startswith('http'):
                        rid = URIRef(id)
                    else:
                        rid = URIRef(f"http://example.com/#{urllib.parse.quote_plus(id)}")

                    for s,p,o in g.triples((None,None,None)):
                        if s:
                            rid = str(s)
                            break

                    g.add((s,DC.identifier,Literal(rid)))
                    if title not in [None, '']:
                        g.add((s,DC.title,Literal(title)))
                    if date not in [None, '']:
                        g.add((s,DC.date,Literal(date)))

                    for s,p,o in g.triples((None,DCTERMS.description,None)):
                        g.add((s,DC.description,o))
                    for s,p,o in g.triples((None,DCTERMS.subject,None)):
                        g.add((s,DC.subject,o))
                    for s,p,o in g.triples((None,DCTERMS.creator,None)):
                        g.add((s,DC.creator,o))

                    metadata_record = etree.fromstring(bytes(g.serialize(format="xml"), 'utf-8'))

                    print(f'parse {id} as turtle')
                except Exception as err:
                    print(f'failed parse as Dublin Core, {err} {traceback.print_stack()}')

                

            else:
                # JSON (mcf?)
                try: 
                    metadata_record = json.loads(recfile)
                    print(f'parse {id} as json, try ld')
                except json.decoder.JSONDecodeError as err:
                    print(f'{id} no turtle -> xml')
                except Exception as err:
                    print(f'failed parse as json, try xml; {err}')
                # XML
                if metadata_record in [None,'']:
                    try:
                        metadata_record = etree.fromstring(recfile)
                        print(f'parse {id} as xml')
                    except etree.XMLSyntaxError as err:
                        print(f'XML document {id} is not well-formed {err}')
                    except Exception as err:
                        print(f'XML document {id} is not string, {err}')
                        metadata_record = etree.fromstring(bytes(recfile, 'utf-8'))

            try:
                record = metadata.parse_record(context, metadata_record, repo)
            except Exception as err:
                print(f'Could not parse {id} as record, {err}, {traceback.print_exc()}')
                continue

            for rec in record:
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
