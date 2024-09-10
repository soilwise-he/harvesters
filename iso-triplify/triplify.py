import lxml.etree as ET
from dotenv import load_dotenv
import sys
sys.path.append('../utils')
from database import dbQuery, dbUQuery
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DC, DCTERMS, RDF, FOAF, SKOS

# Load environment variables from .env file
load_dotenv()

# fetch the mcf's

recs = dbQuery("Select identifier, hash, resultobject, source from harvest.items where resulttype = 'iso19139:2007' and coalesce(turtle,'') = '' and coalesce(error,'') = '' limit 250")

if recs:
    total = len(recs)
    counter = 0
    
    for rec in sorted(recs):
        id, hashcode, resultobject, source = rec
        print(f'Parse identifier {id}')

        # xslURL = "https://raw.githubusercontent.com/SEMICeu/iso-19139-to-dcat-ap/master/iso-19139-to-dcat-ap.xsl"

        # mailto: is no uri -> remove on xslt

        res = resultobject.replace("'","")

        if res.startswith('<?xml'): #remove encoding declaration, assume utf-8; todo in read step
            res = res.split(">",1)[1]

        xml = None
        try:
            xml = ET.fromstring(res)
        except Exception as err:
            print(f'Failed read from string {id}, {err}')

        xsl = ET.parse('iso-19139-to-dcat-ap.xsl')
        rdfxml = None
        ttl = None
        tmerror = None

        if xml:
            transform = ET.XSLT(xsl)
            try:
                rdfxml = ET.tostring(transform(xml), pretty_print=True)
            except:
                tmerror = f'Failed xslt, {id}'
                for error in transform.error_log:
                    tmerror += f'{error.message} {error.line}'
                print(tmerror)

        if rdfxml:
            # convert to ttl
            g = Graph()
            try:
                g.parse(data=rdfxml, format='xml')
                lang = ""
                #select core parameters from graph; language
                for s,p,o in g.triples((None,DCTERMS.language,None)):
                    l = str(o).split('/').pop()
                    if l not in [None,'']:
                        lang=l
                        break

                ttl = g.serialize(format='turtle')
            except Exception as err:
                tmerror = f'Failed serialise {id}, {err}'
                print(f'Failed serialise {id}, {err}')
            
            try: 
                if ttl:
                    recs = dbUQuery(f"update harvest.items set turtle = '{ttl}', language='{lang}' where hash = '{hashcode}'")
            except Exception as err:
                tmerror = f'Failed db update {id}, {err}'
                print(tmerror)
            
            if tmerror:
                recs = dbUQuery(f"update harvest.items set error = '{tmerror}' where hash = '{hashcode}'")

            