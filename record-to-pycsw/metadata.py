
from pycsw.core import config as pconfig
from pycsw.core import metadata, repository, util
from pycsw.core.etree import etree, PARSER
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
                    or identifier like '%%'||i.identifier
                    or identifier = i.uri 
                    or identifier like '%%'||i.uri) 
                order by i.identifier, i.insert_date desc limit 5000""")
loaded_files = []

if recs:
    total = len(recs)
    counter = 0
    
    for rec in sorted(recs):
        id, title, date, turtle_prefix, rtype, resultobject, turtle = rec

        recfile = None
        if rtype in ['SPARQL','HTML']:
            if turtle not in [None,'']:
                if turtle_prefix not in [None,'']:
                    recfile = f"{turtle_prefix}\n\n{turtle}"
                else:
                    recfile = turtle
        else:
            recfile = resultobject
        
        counter += 1
        metadata_record = None

        print(f'Processing record {id} ({counter} of {total})')

        if recfile not in [None,'']:

            if rtype in ['SPARQL','HTML']:
                try:
                    g = Graph()
                    g.parse(data=recfile, format='turtle')

                    # map DCT to DC 
                    elms = ['description','title','subject','publisher','creator','date','type','source','relation','coverage','contributor','rights','format','identifier','language','audience','provenance']
                    for e in elms:
                        for s,p,o in g.triples((None,DCTERMS[e],None)):
                            g.add((s,DC[e],o))
                            g.remove((s,DCTERMS[e],o))

                    # if no title, use from DB  (ESDAC case)
                    if (None,DC.title,None) not in g:
                        g.add((s,DC.title,Literal(title)))
                    # if abstract is empty, use description    
                    if (None,DCTERMS.abstract,None) not in g:
                        for s,p,o in g.triples((None,DC.description,None)):
                            g.add((s,DCTERMS.abstract,o))
                    if (None,DC.identifier,None) not in g:
                        g.add((s,DC.identifier,Literal(id)))

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
                        repo.update(rec)
                        print(f'Updated {id}')
                        loaded_files.append(id)
                    else:
                        print(f'ERROR: {id} not inserted: {err}, {traceback.print_exc()}')

                    #in some cases the origianl id is not the derived id, update it
                    if '' not in [id,rec.identifier] and id != rec.identifier:
                        print(f'updating asynchronous id {id}')
                        dbQuery(f"update {table} set identifier = '{rec.identifier}' where identifier = '{id}'",(),False)
