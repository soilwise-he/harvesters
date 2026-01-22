
from pycsw.core import config as pconfig
from pycsw.core import metadata, repository, util
from pycsw.core.etree import etree, PARSER
from pycsw.core.util import parse_ini_config
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DC, DCTERMS, RDF, FOAF, SKOS
import html, logging
import traceback,urllib
import json, os, psycopg2, sys
sys.path.append('utils')
from database import dbQuery, dbInit

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

logging.getLogger().setLevel(logging.ERROR)

# todo: dublin core parser for json, maybe even use rdflib, ask tom

context = pconfig.StaticContext()
force_update = os.environ.get('force_update') or False

database = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}" 

table = os.environ.get('PYCSW_TABLE') or 'public.records2'

# what if we post to new table, then when done rename new table to old table?
repo = repository.Repository(database, context, table='public.records2')

def parseRDF(md,id,title,rtype,project):

    # CLEAN NEW LINE CHARS FROM XML
    # md = md.replace('\r','').replace('\n','')

    try:
        g = Graph()
        g.parse(data=md.replace('\n\t','').replace('\t',''), format='turtle')
        s = None
        # map DCT to DC 
        elms = ['description','title','subject','publisher','creator','date','type','source','relation','coverage','contributor','rights','format','identifier','language','audience']
        for e in elms:
            for s,p,o in g.triples((None,DCTERMS[e],None)):
                g.add((s,DC[e],o))
                g.remove((s,DCTERMS[e],o))
        if (None,DCTERMS.abstract,None) not in g:
            for s,p,o in g.triples((None,DC.description,None)):
                g.add((s,DCTERMS.abstract,o))
        for s,p,o in g.triples((None,DCTERMS.abstract,None)):
            abs = str(o)
            if '&lt;p&gt;' in abs:
                try: 
                    abs = html.unescape(abs)
                    g.set((s, DCTERMS.abstract, Literal(abs)))
                except:
                    print("Failed parsing encoded html",abs)
            if '\n' in abs or '\r' in abs:
                g.set((s, DCTERMS.abstract, Literal(abs.replace('\n',' ').replace('\r',' '))))
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
                if rtype not in [None,'']:
                    g.add((s,DC.type,Literal(rtype)))
                else:
                    g.add((s,DC.type,Literal('unknown')))
            if str(s).startswith('http'):
                g.add((s,DCTERMS.references,Literal(URIRef(str(s)))))
            #if len(str(id).split('/')) == 2:
            #    g.add((s,DC.relation,Literal(f'http://doi.org/{str(id)}')))

        # project workaround
        if project not in [None,'']:
             g.add((s,DCTERMS.relation,Literal(project)))

        return etree.fromstring(bytes(g.serialize(format="xml"), 'utf-8'))

    except Exception as err:
        print(f'failed parse as Dublin Core, {err}')

# clean up temporary public.records2 table first
try:
    dbQuery("""truncate public.records2""",(),False)
except:
    None

# get records to be imported from db (updated after xxx?) or "where id not in (select id from records)"
# if failed, save as failed, not ask again, or maybe later
recs = dbQuery("""select DISTINCT ON (i.identifier) i.identifier, i.title, i.date, s.turtle_prefix, s.type, i.resultobject, i.resulttype, i.itemtype, i.turtle, i.project 
                from harvest.items i, harvest.sources s 
                where coalesce(i.identifier,'') <> '' 
                and (lower(resulttype) ='iso19139:2007' or coalesce(turtle,'') <> '')
                and i.source = s.name""",(),True)
loaded_files = []

if recs:
    total = len(recs)
    print('Process',total,'records')
    counter = 0
    failed_counter = 0
    uniqueRecords = []
    cnt = 0
    for rec in sorted(recs):
        id, title, date, turtle_prefix, rtype, resultobject, rectype, restype, turtle, project = rec
        cnt = cnt+1
 #       print(cnt,id,rectype)
        counter += 1
        metadata_record = None

        # for now keep iso records as is
        if rectype and rectype.lower() in ['iso19139', 'iso19139:2007', 'iso19115']:
            # import as xml
            recfile = resultobject
            try:
                metadata_record = etree.fromstring(recfile)
            except etree.XMLSyntaxError as err:
                print(f'ERROR: XML document {id} is not well-formed {err}')
            except Exception as err:
                try:
                    metadata_record = etree.fromstring(bytes(recfile, 'utf-8'))
                except Exception as err:
                    print(f'Error: Failed parsing iso XML {id}, {err}')
        elif turtle not in [None,'']: 
            # print(f'{counter}. Parse {id} as rdf ({restype})')  
            # import as Dublin Core
            recfile = turtle
            if turtle_prefix not in [None,'']: # identify if prefix is needed
                recfile = f"{turtle_prefix}\n\n{turtle}"
            metadata_record = parseRDF(recfile,id,title,restype,project)
        else: 
            print(f'ERROR: Can not parse {id}', rectype)

        # insert into repo
        try:
            if metadata_record not in [None,'']:
                record = metadata.parse_record(context, metadata_record, repo)
                for rec in record:
                    if rec.identifier and rec.identifier not in uniqueRecords:
                        dt = util.get_today_and_now()
                        if hasattr(rec,'date') and rec.date not in [None,'']:
                            dt = rec.date
                        try:
                            repo.insert(rec, 'local', dt)
                            loaded_files.append(id)
                            uniqueRecords.append(rec.identifier)
                            # in some cases the origianl id is not the derived id, add it to identifier2
                            dbQuery(f"update harvest.items set identifier2 = %s where identifier = %s",(rec.identifier,id),False)
                        except Exception as err:
                            print('Record',id,'failed',err)
                    else:
                        print('Record',id,'skipped, final-id',rec.identifier,'already in database')

        except Exception as err:
            print(f'Error: Could not parse {id} as record, {err}')
            continue

print('Prepare finished, move to records')
conn = dbInit()
cursor = conn.cursor()
cursor.execute("truncate table public.records")   

cursor.execute("""insert into public.records select
    distinct on (r.identifier) r.identifier, typename, schema, mdsource, insert_date, xml, anytext, metadata, metadata_type, language, type, 
    coalesce((select max(target) from harvest.translations where source=r.title),r.title) as title, title_alternate,
    coalesce((select max(target) from harvest.translations where source=r.abstract),r.abstract) as abstract, 
    edition, keywords, keywordstype, themes, parentidentifier, relation, time_begin, time_end, topicategory, resourcelanguage, creator, 
    publisher, contributor, organization, securityconstraints, accessconstraints, otherconstraints, 
    date, date_revision, date_creation, date_publication, date_modified, format, source, crs, 
    geodescode, denominator, distancevalue, distanceuom, wkt_geometry, servicetype, 
    servicetypeversion, operation, couplingtype, operateson, operatesonidentifier, operatesoname, 
    degree, classification, conditionapplyingtoaccessanduse, lineage, responsiblepartyrole, 
    specificationtitle, specificationdate, specificationdatetype, platform, instrument, sensortype, 
    cloudcover, bands, links, contacts, anytext_tsvector, wkb_geometry, 
    k.soil_functions, k.soil_physical_properties, k.productivity, k.soil_services, k.soil_classification, k.soil_processes, 
    k.soil_biological_properties, k.contamination, k.soil_properties, k.soil_threats, k.ecosystem_services, 
    k.soil_chemical_properties, k.soil_management, illuminationelevationangle
    from public.records2 r left join public.keywords_temp k on r.identifier = k.identifier""")

# element matcher on type
cursor.execute("""UPDATE public.records r SET type = a.value FROM harvest.augmentation a WHERE r.identifier = a.identifier AND a.element_type = 'type';""")
cursor.execute("""UPDATE public.records SET type = NULL WHERE identifier NOT IN (SELECT DISTINCT identifier FROM harvest.augmentation WHERE element_type = 'type');""")
# workaround for '//' to '/' bahavior
cursor.execute("""UPDATE public.records pr set identifier = MD5(identifier) where identifier like '%//%' and NOT EXISTS (SELECT 1 FROM public.records WHERE identifier = MD5(pr.identifier));""")

conn.commit()  

print('Inserted',len(uniqueRecords),'records')