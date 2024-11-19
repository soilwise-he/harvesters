import lxml.etree as ET

from dotenv import load_dotenv
import sys
sys.path.append('utils')
from database import dbQuery, dbUQuery
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DC, DCTERMS, RDF, FOAF, SKOS

# Load environment variables from .env file
load_dotenv()

count=2500

class LinkResolver(ET.Resolver):
    def resolve(self, url, id, context):
        return self.resolve_string(
            '<!ENTITY myentity "[resolved text: %s]">' % url, context)


# fetch the mcf's
recs = dbQuery(f"Select identifier, hash, resultobject, source from harvest.items where resulttype = 'iso19139:2007' and coalesce(turtle,'') = '' and coalesce(error,'') = '' limit {count}")

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


        iso_parser = ET.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        iso_parser.resolvers.add( LinkResolver() )
        #xsl = ET.parse(StringIO(open('iso-triplify/iso-19139-to-dcat-ap.xsl', "r").read().encode('utf-8')), iso_parser)
        xsl = ET.fromstring(open('iso-triplify/iso-19139-to-dcat-ap.xsl', "r").read().encode('utf-8'), parser=iso_parser)

        #xsl = ET.parse('iso-triplify/iso-19139-to-dcat-ap.xsl')
        rdfxml = None
        ttl = None
        tmerror = None

        if xml not in [None,'']:
            #ac = ET.XSLTAccessControl(read_network=False, read_file=False)
            transform = ET.XSLT(xsl)#, access_control=ac)
            try:
                rdfxml = ET.tostring(transform(xml), pretty_print=True)
                print(transform.error_log)
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
                # what is my id?
                sj = None
                for s,p,o in g.triples((None,DCTERMS.identifier,None)):
                    sj = s
                    break
                #append source
                if sj:
                    g.add((sj,DCTERMS.isReferencedBy,Literal(source)))
                
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

