
from pycsw.core import config as pconfig
from pycsw.core import metadata, repository, util
from pycsw.core.etree import etree, PARSER
from pycsw.core.util import parse_ini_config
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DC, DCTERMS, RDF, FOAF, SKOS
import traceback,urllib
import json, os, psycopg2, sys
sys.path.append('utils')
from database import dbQuery

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# todo: dublin core parser for json, maybe even use rdflib, ask tom

context = pconfig.StaticContext()
force_update = os.environ.get('force_update') or False

database = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}" 

table = os.environ.get('PYCSW_TABLE') or 'public.records2'

# what if we post to new table, then when done rename new table to old table?
repo = repository.Repository(database, context, table='public.records2')

def parseRDF(md,id,title):
    try:
        g = Graph()
        g.parse(data=md, format='turtle')

        # map DCT to DC 
        elms = ['description','title','subject','publisher','creator','date','type','source','relation','coverage','contributor','rights','format','identifier','language','audience','provenance']
        for e in elms:
            for s,p,o in g.triples((None,DCTERMS[e],None)):
                g.add((s,DC[e],o))
                g.remove((s,DCTERMS[e],o))
        if (None,DCTERMS.abstract,None) not in g:
            for s,p,o in g.triples((None,DC.description,None)):
                g.add((s,DCTERMS.abstract,o))
        for s,p,o in g.triples((None,DC.identifier,None)):
            id2 = str(o)
            if id2.startswith('http'):
                g.add((s,DCTERMS.references,Literal(URIRef(id2))))
            elif id2.startswith('10.'):
                g.add((s,DCTERMS.references,Literal(f'https://doi.org/{id2}')))
        
        if s:
            # if no title, use from DB  (ESDAC case)
            if (None,DC.title,None) not in g:
                g.add((s,DC.title,Literal(title)))
            # if abstract is empty, use description    
            if (None,DC.identifier,None) not in g:
                g.add((s,DC.identifier,Literal(id)))
            if (None,DC.type,None) not in g:
                g.add((s,DC.type,Literal('document')))
            #if len(str(id).split('/')) == 2:
            #    g.add((s,DC.relation,Literal(f'http://doi.org/{str(id)}')))
            
        return etree.fromstring(bytes(g.serialize(format="xml"), 'utf-8'))

    except Exception as err:
        print(f'failed parse as Dublin Core, {err} {traceback.print_stack()}')


# clean up public table first
try:
    dbQuery("""truncate public.records2""",(),False)
except:
    None

# get records to be imported from db (updated after xxx?) or "where id not in (select id from records)"
# if failed, save as failed, not ask again, or maybe later
recs = dbQuery("""select DISTINCT ON (i.identifier) i.identifier, i.title, i.date, s.turtle_prefix, s.type, i.resultobject, i.resulttype, i.turtle 
                from harvest.items i, harvest.sources s 
                where coalesce(i.identifier,'') <> '' 
                and (lower(resulttype) ='iso19139:2007' or coalesce(turtle,'') <> '')
                and i.source = s.name""",(),True)
loaded_files = []

if recs:
    total = len(recs)
    counter = 0
    failed_counter = 0
    
    for rec in sorted(recs):
        id, title, date, turtle_prefix, rtype, resultobject, restype, turtle = rec

        counter += 1
        metadata_record = None

        # for now keep iso records as is
        if restype and restype.lower() in ['iso19139', 'iso19139:2007', 'iso19115']:
            # import as xml
            recfile = resultobject
            try:
                print(f'{counter}. parse {id} as xml')
                metadata_record = etree.fromstring(recfile)
            except etree.XMLSyntaxError as err:
                print(f'ERROR: XML document {id} is not well-formed {err}')
            except Exception as err:
                print(f'WARNING: XML parsing as string {id} failed, {err}')
                try:
                    metadata_record = etree.fromstring(bytes(recfile, 'utf-8'))
                except Exception as err:
                    print(f'Error: Failed parsing XML {id}, {err} {traceback.print_exc()}')
        elif turtle not in [None,'']: 
            print(f'{counter}. parse {id} as rdf')  
            # import as Dublin Core
            recfile = turtle
            if turtle_prefix not in [None,'']: # identify if prefix is needed
                recfile = f"{turtle_prefix}\n\n{turtle}"
            metadata_record = parseRDF(recfile,id,title)
        else: 
            print(f'ERROR: Can not parse {id}')

        # insert into repo
        try:
            if metadata_record not in [None,'']:
                record = metadata.parse_record(context, metadata_record, repo)
                for rec in record:
                    try:
                        repo.insert(rec, 'local', util.get_today_and_now())
                        loaded_files.append(id)
                    except Exception as err:
                        if force_update:
                            repo.update(rec)
                            print(f'Updated {id}')
                            loaded_files.append(id)
                        else:
                            print(f'ERROR: {id} not inserted: {err}, {traceback.print_exc()}')

                        # in some cases the origianl id is not the derived id, update it
                        if '' not in [id,rec.identifier] and id != rec.identifier:
                            print(f'updating asynchronous id {id}')
                            dbQuery(f"update {table} set identifier = '{rec.identifier}' where identifier = %s",(id),False)
        except Exception as err:
            print(f'Error: Could not parse {id} as record, {err}, {traceback.print_exc()}')
            continue

        
# workaround for '//' to '/' bahavior
dbQuery("""UPDATE public.records2 set identifier = replace(identifier,'//','/') where identifier like %s""",('%//%',),False)
# copy to temp table, then rename it
dbQuery("""truncate table public.records""",(),False)
dbQuery("""insert into public.records select * from public.records2""",(),False)


