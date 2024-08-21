from owslib.csw import CswRecord
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DC, DCTERMS, RDF, FOAF, SKOS
from pycsw.core.etree import etree, PARSER

rec = '''
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix schema: <https://schema.org/> .

<https://esdac.jrc.ec.europa.eu//images/Eudasm/latinamerica/images/maps/download/br12042_so.jpg> dcterms:creator "Carvalho, J.S., Oliveira, L.F. " ;
    dcterms:date "1972" ;
    dcterms:identifier "https://esdac.jrc.ec.europa.eu//images/Eudasm/latinamerica/images/maps/download/br12042_so.jpg" ;
    dcterms:publisher "Divisao de Pesquisa Pedologica, Rio de Janeiro. " ;
    dcterms:relation "https://esdac.jrc.ec.europa.eu//images/Eudasm/latinamerica/images/maps/download/PDF/br12042_so.pdf",
        "https://esdac.jrc.ec.europa.eu//images/Eudasm/latinamerica/images/maps/download/br12042_so.jpg" ;
    dcterms:subject "Brazil",
        "Maps",
        "Maps & Documents",
        "National Soil Maps (EUDASM)",
        "South America" ;
    dcterms:title "Mapa Exploratório dos Solos. Mapa Basico: USAF Operational Navigation Chart. Folha ONC-27." ;
    dcterms:type "dataset" ;
    schema:thumbnailUrl "https://esdac.jrc.ec.europa.eu//images/Eudasm/latinamerica/images/maps/download/ico/br12042_so.jpg" .

'''

g = Graph()
g.parse(data=rec, format='turtle')
# map DCT to DC 
elms = ['description','title','subject','publisher','creator','date','type','source','relation','coverage','contributor','rights','format','identifier','language','audience','provenance']
for e in elms:
    for s,p,o in g.triples((None,DCTERMS[e],None)):
        g.add((s,DC[e],o))
        g.remove((s,DCTERMS[e],o))

metadata_record = etree.fromstring(bytes(g.serialize(format="xml"), 'utf-8'))
md = CswRecord(metadata_record)

print(md.__dict__)
print(md.identifier)