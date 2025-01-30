**CORDIS uses EURIO: EUropean Research Information Ontology.** https://op.europa.eu/en/web/eu-vocabularies/dataset/-/resource?uri=http://publications.europa.eu/resource/dataset/eurio

The UML: https://git.wur.nl/soilwise/soilwise-docs/-/wikis/uploads/28e281900fb54e106518919ccdeec9a4/CordisProjectUML.png
**STEP 1. LOAD TITLE OF PROJECTS AND DOI AND TITLE OF PPROJECT PUBLICATIONS FROM CORDIS INTO VIRTUOSO: 2598 HITS**

**First try was to query CORDIS for Publications of Projects from a certain Funding Scheme. This resulted in 0 (Zero) results as it turned out the Funding Scheme has not been filled for soil-related projects.**

There are 31 Funding Schemes with **soil** in the title:

```
PREFIX eurio:<http://data.europa.eu/s66#>
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
PREFIX ns: <http://example.com/namespace>
SELECT distinct ?fundingschemetitle 
WHERE
{
  ?fundingscheme a eurio:FundingScheme.
  ?fundingscheme eurio:title ?fundingschemetitle.
  FILTER regex(?fundingschemetitle, "soil", "i")
}
```

However, when searching for Projects within these fundingschemes there are no hits:

```
PREFIX eurio:<http://data.europa.eu/s66#>
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
PREFIX ns: <http://example.com/namespace>
SELECT distinct ?fundingschemetitle ?projecttitle ?publicationdoi
WHERE
{
  ?project a eurio:Project.
  ?project eurio:title ?projecttitle. 
  optional {   ?project eurio:hasResult/eurio:doi ?publicationdoi. }
  ?project eurio:isFundedBy/eurio:hasFundingSchemeProgramme/eurio:title ?fundingschemetitle.
   FILTER regex(?fundingschemetitle, "soil", "i")
}
```

**N.b. you will find hits when using a different search text, i.e. "generation"**

**Query CORDIS to load Title of Projects into VIRTUOSO. The Projects do have ProjectPublications and in CORDIS they have "Soil" as part of the abstract.**

```
PREFIX eurio: <http://data.europa.eu/s66#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
CONSTRUCT {
  ?identifierURI dcterms:title ?title
}
WHERE
{
  ?project a eurio:Project.
  ?project eurio:title ?title.
  ?project eurio:abstract ?abstract.
  ?project eurio:identifier ?identifier.
  BIND(IRI(CONCAT("https://cordis.europa.eu/project/id/", ?identifier)) AS ?identifierURI).
  ?project eurio:hasResult ?result.
  ?result rdf:type ?type.
  optional { ?result eurio:doi ?doi } .
  ?result eurio:title ?restitle.
  FILTER regex(?type, eurio:ProjectPublication)
#  FILTER regex(?type, eurio:JournalPaper)
  FILTER ((regex(?abstract, "Soil", "i")) || (?identifier = "676982"^^<http://www.w3.org/2000/01/rdf-schema#Literal>)|| (?identifier = "867468"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier =  "101006717"^^<http://www.w3.org/2000/01/rdf-schema#Literal> ))
}
```

Based on the CORDIS generated CURL request the generated URL is loaded into virtuoso directly at graph "https://soilwise-he.github.io/soil-health"

**CURL-generated http-request to retrieve Titles**:
```
https://cordis.europa.eu/datalab/sparql?query=PREFIX%20eurio%3A%20%3Chttp%3A%2F%2Fdata.europa.eu%2Fs66%23%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20dcterms%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0ACONSTRUCT%20%7B%0A%20%20%3FidentifierURI%20dcterms%3Atitle%20%3Ftitle%0A%7D%0AWHERE%0A%7B%0A%20%20%3Fproject%20a%20eurio%3AProject.%0A%20%20%3Fproject%20eurio%3Atitle%20%3Ftitle.%0A%20%20%3Fproject%20eurio%3Aabstract%20%3Fabstract.%0A%20%20%3Fproject%20eurio%3Aidentifier%20%3Fidentifier.%0A%20%20BIND%28IRI%28CONCAT%28%22https%3A%2F%2Fcordis.europa.eu%2Fproject%2Fid%2F%22%2C%20%3Fidentifier%29%29%20AS%20%3FidentifierURI%29.%0A%20%20%3Fproject%20eurio%3AhasResult%20%3Fresult.%0A%20%20%3Fresult%20rdf%3Atype%20%3Ftype.%0A%20%20optional%20%7B%20%3Fresult%20eurio%3Adoi%20%3Fdoi%20%7D%20.%0A%20%20%3Fresult%20eurio%3Atitle%20%3Frestitle.%0A%20%20FILTER%20regex%28%3Ftype%2C%20eurio%3AProjectPublication%29%0A%23%20%20FILTER%20regex%28%3Ftype%2C%20eurio%3AJournalPaper%29%0A%20%20FILTER%20%28%28regex%28%3Fabstract%2C%20%22Soil%22%2C%20%22i%22%29%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%22676982%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%7C%7C%20%28%3Fidentifier%20%3D%20%22867468%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%20%22101006717%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%20%29%29%0A%7D
```

**Some addiotional ESDAC projects by the FILTER part**:
```
 (?identifier = "676982"^^<http://www.w3.org/2000/01/rdf-schema#Literal>)  || (?identifier = "867468"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier =  "101006717"^^<http://www.w3.org/2000/01/rdf-schema#Literal> )
```


**Query CORDIS to load RCN numbers of Projects into VIRTUOSO. The Projects do have ProjectPublications and in CORDIS they have "Soil" as part of the abstract.**

```
PREFIX eurio: <http://data.europa.eu/s66#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
CONSTRUCT {
  ?identifierURI eurio:rcn ?rcn
}
WHERE
{
  ?project a eurio:Project.
  ?project eurio:title ?title.
  ?project eurio:rcn ?rcn.
  ?project eurio:identifier ?identifier.
  BIND(IRI(CONCAT("https://cordis.europa.eu/project/id/", ?identifier)) AS ?identifierURI).
  ?project eurio:abstract ?abstract.
  ?project eurio:hasResult ?result.
  ?result eurio:doi ?doi.
  FILTER ((regex(?abstract, "Soil", "i")) || (?identifier = "676982"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier = "867468"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier =  "101006717"^^<http://www.w3.org/2000/01/rdf-schema#Literal> ))
}
```

**CURL-generated http-request to retrieve RCN numbers**:

```
https://cordis.europa.eu/datalab/sparql?query=PREFIX%20eurio%3A%20%3Chttp%3A%2F%2Fdata.europa.eu%2Fs66%23%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20dcterms%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0ACONSTRUCT%20%7B%0A%20%20%3FidentifierURI%20eurio%3Arcn%20%3Frcn%0A%7D%0AWHERE%0A%7B%0A%20%20%3Fproject%20a%20eurio%3AProject.%0A%20%20%3Fproject%20eurio%3Atitle%20%3Ftitle.%0A%20%20%3Fproject%20eurio%3Arcn%20%3Frcn.%0A%20%20%3Fproject%20eurio%3Aidentifier%20%3Fidentifier.%0A%20%20BIND%28IRI%28CONCAT%28%22https%3A%2F%2Fcordis.europa.eu%2Fproject%2Fid%2F%22%2C%20%3Fidentifier%29%29%20AS%20%3FidentifierURI%29.%0A%20%20%3Fproject%20eurio%3Aabstract%20%3Fabstract.%0A%20%20%3Fproject%20eurio%3AhasResult%20%3Fresult.%0A%20%20%3Fresult%20eurio%3Adoi%20%3Fdoi.%0A%20%20FILTER%20%28%28regex%28%3Fabstract%2C%20%22Soil%22%2C%20%22i%22%29%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%22676982%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%22867468%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%20%22101006717%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%20%29%29%0A%7D
```

**Query CORDIS to load Organisations which contribute to Projects into VIRTUOSO. The Projects do have ProjectPublications and in CORDIS they have "Soil" as part of the abstract.**

```
PREFIX eurio: <http://data.europa.eu/s66#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dct: <http://purl.org/dc/terms/>
construct { 
  ?identifierURI dct:contributor ?name
}
WHERE
{
  ?role a eurio:OrganisationRole.
  ?role eurio:isInvolvedIn ?project.
  ?role eurio:isRoleOf ?organiation.
  ?organiation eurio:legalName ?name.
  ?project eurio:identifier ?identifier.
  BIND(IRI(CONCAT("https://cordis.europa.eu/project/id/", ?identifier)) AS ?identifierURI).
  ?project eurio:abstract ?abstract.
  ?project eurio:hasResult ?result.
  ?result eurio:doi ?doi.
  FILTER ((regex(?abstract, "Soil", "i")) || (?identifier = "676982"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier = "867468"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier =  "101006717"^^<http://www.w3.org/2000/01/rdf-schema#Literal> ))
}
```

**CURL-generated http-request to retrieve Organistion names**:
```
https://cordis.europa.eu/datalab/sparql?query=PREFIX%20eurio%3A%20%3Chttp%3A%2F%2Fdata.europa.eu%2Fs66%23%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20dct%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0Aconstruct%20%7B%20%0A%20%20%3FidentifierURI%20dct%3Acontributor%20%3Fname%0A%7D%0AWHERE%0A%7B%0A%20%20%3Frole%20a%20eurio%3AOrganisationRole.%0A%20%20%3Frole%20eurio%3AisInvolvedIn%20%3Fproject.%0A%20%20%3Frole%20eurio%3AisRoleOf%20%3Forganiation.%0A%20%20%3Forganiation%20eurio%3AlegalName%20%3Fname.%0A%20%20%3Fproject%20eurio%3Aidentifier%20%3Fidentifier.%0A%20%20BIND%28IRI%28CONCAT%28%22https%3A%2F%2Fcordis.europa.eu%2Fproject%2Fid%2F%22%2C%20%3Fidentifier%29%29%20AS%20%3FidentifierURI%29.%0A%20%20%3Fproject%20eurio%3Aabstract%20%3Fabstract.%0A%20%20%3Fproject%20eurio%3AhasResult%20%3Fresult.%0A%20%20%3Fresult%20eurio%3Adoi%20%3Fdoi.%0A%20%20FILTER%20%28%28regex%28%3Fabstract%2C%20%22Soil%22%2C%20%22i%22%29%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%22676982%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%22867468%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%20%22101006717%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%20%29%29%0A%7D
```

**Query CORDIS to load Project Acronyms into VIRTUOSO. The Projects do have ProjectPublications and in CORDIS they have "Soil" as part of the abstract.**

 ```
PREFIX eurio: <http://data.europa.eu/s66#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
construct { 
  ?s dcterms:alternative ?acronym
}    
WHERE
{
  ?project a eurio:Project.
      ?acr a eurio:Acronym. 
      ?acr eurio:shortForm ?acronym. 
      ?acr eurio:definition ?def.
  ?project eurio:title ?title.
  ?project eurio:identifier ?identifier.
  BIND(IRI(CONCAT("https://cordis.europa.eu/project/id/", ?identifier)) AS ?s).
  ?project eurio:abstract ?abstract.
  ?project eurio:hasResult ?result.
  ?result eurio:doi ?doi.
  FILTER (?def =?title)
  FILTER ((regex(?abstract, "Soil", "i")) || (?identifier = "676982"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier = "867468"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier =  "101006717"^^<http://www.w3.org/2000/01/rdf-schema#Literal> ))
}
```

**CURL-generated http-request to retrieve Acronyms**:

```
https://cordis.europa.eu/datalab/sparql?query=PREFIX%20eurio%3A%20%3Chttp%3A%2F%2Fdata.europa.eu%2Fs66%23%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20dcterms%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0Aconstruct%20%7B%20%0A%20%20%3Fs%20dcterms%3Aalternative%20%3Facronym%0A%7D%20%20%20%20%0AWHERE%0A%7B%0A%20%20%3Fproject%20a%20eurio%3AProject.%0A%20%20%20%20%20%20%3Facr%20a%20eurio%3AAcronym.%20%0A%20%20%20%20%20%20%3Facr%20eurio%3AshortForm%20%3Facronym.%20%0A%20%20%20%20%20%20%3Facr%20eurio%3Adefinition%20%3Fdef.%0A%20%20%3Fproject%20eurio%3Atitle%20%3Ftitle.%0A%20%20%3Fproject%20eurio%3Aidentifier%20%3Fidentifier.%0A%20%20BIND%28IRI%28CONCAT%28%22https%3A%2F%2Fcordis.europa.eu%2Fproject%2Fid%2F%22%2C%20%3Fidentifier%29%29%20AS%20%3Fs%29.%0A%20%20%3Fproject%20eurio%3Aabstract%20%3Fabstract.%0A%20%20%3Fproject%20eurio%3AhasResult%20%3Fresult.%0A%20%20%3Fresult%20eurio%3Adoi%20%3Fdoi.%0A%20%20FILTER%20%28%3Fdef%20%3D%3Ftitle%29%0A%20%20FILTER%20%28%28regex%28%3Fabstract%2C%20%22Soil%22%2C%20%22i%22%29%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%22676982%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%22867468%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%20%22101006717%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%20%29%29%0A%7D
```

**Query CORDIS to load DOIs of Project Publications into VIRTUOSO where the Projects in CORDIS have "Soil" as part of the abstract.**

```
PREFIX eurio:<http://data.europa.eu/s66#>
PREFIX datacite: <http://purl.org/spar/datacite/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
CONSTRUCT {
  ?result datacite:doi ?doi .
} WHERE
{
  ?project a eurio:Project.
  ?project eurio:abstract ?abstract.
  ?project eurio:hasResult ?result.
  ?result rdf:type ?type.
  ?result eurio:doi ?doi.
  FILTER regex(?type, eurio:ProjectPublication)
  FILTER ((regex(?abstract, "Soil", "i")) || (?identifier = "676982"^^<http://www.w3.org/2000/01/rdf-schema#Literal>)  || (?identifier = "867468"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier =  "101006717"^^<http://www.w3.org/2000/01/rdf-schema#Literal> ))
}
```
Or with DOI as URI
```
PREFIX eurio:<http://data.europa.eu/s66#>
PREFIX datacite: <http://purl.org/spar/datacite/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
CONSTRUCT {
  ?result datacite:doi ?doiURI
} WHERE
{
  ?project a eurio:Project.
  ?project eurio:abstract ?abstract.
  ?project eurio:identifier ?identifier.
  ?project eurio:hasResult ?result.
  ?result rdf:type ?type.
  ?result eurio:doi ?doi.
  BIND(IRI(CONCAT("https://doi.org/", ?doi)) AS ?doiURI).
  FILTER regex(?type, eurio:ProjectPublication)
  FILTER ((regex(?abstract, "Soil", "i")) || (?identifier = "676982"^^<http://www.w3.org/2000/01/rdf-schema#Literal>)  || (?identifier = "867468"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier =  "101006717"^^<http://www.w3.org/2000/01/rdf-schema#Literal> ))
}
```

This results in 2598 hits.

And now the other way round

```
PREFIX eurio:<http://data.europa.eu/s66#>
PREFIX datacite: <http://purl.org/spar/datacite/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
CONSTRUCT {
  ?doiURI eurio:ProjectPublication ?result .
} WHERE
{
  ?project a eurio:Project.
  ?project eurio:abstract ?abstract.
  ?project eurio:identifier ?identifier.
  ?project eurio:hasResult ?result.
  ?result rdf:type ?type.
  ?result eurio:doi ?doi.
  BIND(IRI(CONCAT("https://doi.org/", ?doi)) AS ?doiURI).
  FILTER regex(?type, eurio:ProjectPublication)
  FILTER ((regex(?abstract, "Soil", "i")) || (?identifier = "676982"^^<http://www.w3.org/2000/01/rdf-schema#Literal>)  || (?identifier = "867468"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier =  "101006717"^^<http://www.w3.org/2000/01/rdf-schema#Literal> ))
}
```

Based on the CORDIS generated CURL request the generated URL is loaded into virtuoso directly at graph "https://soilwise-he.github.io/soil-health"

**CURL-generated http-request to retrieve DOIs**:

```
https://cordis.europa.eu/datalab/sparql?query=PREFIX%20eurio%3A%3Chttp%3A%2F%2Fdata.europa.eu%2Fs66%23%3E%0APREFIX%20datacite%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fspar%2Fdatacite%2F%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0ACONSTRUCT%20%7B%0A%20%20%3FdoiURI%20eurio%3AProjectPublication%20%3Fresult%20.%0A%7D%20WHERE%0A%7B%0A%20%20%3Fproject%20a%20eurio%3AProject.%0A%20%20%3Fproject%20eurio%3Aabstract%20%3Fabstract.%0A%20%20%3Fproject%20eurio%3Aidentifier%20%3Fidentifier.%0A%20%20%3Fproject%20eurio%3AhasResult%20%3Fresult.%0A%20%20%3Fresult%20rdf%3Atype%20%3Ftype.%0A%20%20%3Fresult%20eurio%3Adoi%20%3Fdoi.%0A%20%20BIND%28IRI%28CONCAT%28%22https%3A%2F%2Fdoi.org%2F%22%2C%20%3Fdoi%29%29%20AS%20%3FdoiURI%29.%0A%20%20FILTER%20regex%28%3Ftype%2C%20eurio%3AProjectPublication%29%0A%20%20FILTER%20%28%28regex%28%3Fabstract%2C%20%22Soil%22%2C%20%22i%22%29%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%22676982%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%20%7C%7C%20%28%3Fidentifier%20%3D%20%22867468%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%20%22101006717%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%20%29%29%0A%7D
```


**Query CORDIS to load TITLES of Project Publications into VIRTUOSO where the Projects in CORDIS have "Soil" as part of the abstract.**

**Remark: Use the doi as subject**

```
PREFIX eurio:<http://data.europa.eu/s66#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
CONSTRUCT {
  ?doiURI dcterms:title ?title
}
WHERE
{
  ?project a eurio:Project.
  ?project eurio:abstract ?abstract.
  ?project eurio:identifier ?identifier.
  ?project eurio:hasResult ?result.
  ?result rdf:type ?type.
  ?result eurio:doi ?doi.
  BIND(IRI(CONCAT("https://doi.org/", ?doi)) AS ?doiURI).
  ?result eurio:title ?title.
  FILTER ((regex(?abstract, "Soil", "i")) || (?identifier = "676982"^^<http://www.w3.org/2000/01/rdf-schema#Literal>)  || (?identifier = "867468"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier =  "101006717"^^<http://www.w3.org/2000/01/rdf-schema#Literal> ))
  FILTER regex(?type, eurio:ProjectPublication)
}
```

And again load the result into virtuoso directly at graph "https://soilwise-he.github.io/soil-health" by using the CORDIS generated CURL request.

**CURL-generated http-request to retrieve TITLES:**

```
https://cordis.europa.eu/datalab/sparql?query=PREFIX%20eurio%3A%3Chttp%3A%2F%2Fdata.europa.eu%2Fs66%23%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20dcterms%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0ACONSTRUCT%20%7B%0A%20%20%3FdoiURI%20dcterms%3Atitle%20%3Ftitle%0A%7D%0AWHERE%0A%7B%0A%20%20%3Fproject%20a%20eurio%3AProject.%0A%20%20%3Fproject%20eurio%3Aidentifier%20%3Fidentifier.%0A%20%20%3Fproject%20eurio%3Aabstract%20%3Fabstract.%0A%20%20%3Fproject%20eurio%3AhasResult%20%3Fresult.%0A%20%20%3Fresult%20rdf%3Atype%20%3Ftype.%0A%20%20%3Fresult%20eurio%3Adoi%20%3Fdoi.%0A%20%20BIND%28IRI%28CONCAT%28%22https%3A%2F%2Fdoi.org%2F%22%2C%20%3Fdoi%29%29%20AS%20%3FdoiURI%29.%0A%20%20%3Fresult%20eurio%3Atitle%20%3Ftitle.%0A%20%20FILTER%20%28%28regex%28%3Fabstract%2C%20%22Soil%22%2C%20%22i%22%29%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%22676982%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%20%7C%7C%20%28%3Fidentifier%20%3D%20%22867468%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%20%22101006717%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%20%29%29%0A%20%20FILTER%20regex%28%3Ftype%2C%20eurio%3AProjectPublication%29%0A%7D
```

**Establish the link between the PROJECT and the PROJECTPUBLICATION**
```
PREFIX eurio: <http://data.europa.eu/s66#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
CONSTRUCT {
  ?identifierURI eurio:hasResult ?doiURI
}
WHERE
{
  ?project a eurio:Project.
  ?project eurio:title ?title.
  ?project eurio:identifier ?identifier.
  BIND(IRI(CONCAT("https://cordis.europa.eu/project/id/", ?identifier)) AS ?identifierURI).
  ?project eurio:abstract ?abstract.
  ?project eurio:hasResult ?result.
  ?result rdf:type ?type.
  ?result eurio:doi ?doi.
  BIND(IRI(CONCAT("https://doi.org/", ?doi)) AS ?doiURI).
  FILTER ((regex(?abstract, "Soil", "i")) || (?identifier = "676982"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier = "867468"^^<http://www.w3.org/2000/01/rdf-schema#Literal>) || (?identifier =  "101006717"^^<http://www.w3.org/2000/01/rdf-schema#Literal> ))
}
```

And load the result into virtuoso directly at graph "https://soilwise-he.github.io/soil-health" by using the CORDIS generated CURL request.

**CURL-generated http-request:**

```
https://cordis.europa.eu/datalab/sparql?query=PREFIX%20eurio%3A%20%3Chttp%3A%2F%2Fdata.europa.eu%2Fs66%23%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20dcterms%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0ACONSTRUCT%20%7B%0A%20%20%3FidentifierURI%20eurio%3AhasResult%20%3FdoiURI%0A%7D%0AWHERE%0A%7B%0A%20%20%3Fproject%20a%20eurio%3AProject.%0A%20%20%3Fproject%20eurio%3Atitle%20%3Ftitle.%0A%20%20%3Fproject%20eurio%3Aidentifier%20%3Fidentifier.%0A%20%20BIND%28IRI%28CONCAT%28%22https%3A%2F%2Fcordis.europa.eu%2Fproject%2Fid%2F%22%2C%20%3Fidentifier%29%29%20AS%20%3FidentifierURI%29.%0A%20%20%3Fproject%20eurio%3Aabstract%20%3Fabstract.%0A%20%20%3Fproject%20eurio%3AhasResult%20%3Fresult.%0A%20%20%3Fresult%20rdf%3Atype%20%3Ftype.%0A%20%20%3Fresult%20eurio%3Adoi%20%3Fdoi.%0A%20%20BIND%28IRI%28CONCAT%28%22https%3A%2F%2Fdoi.org%2F%22%2C%20%3Fdoi%29%29%20AS%20%3FdoiURI%29.%0A%20%20FILTER%20%28%28regex%28%3Fabstract%2C%20%22Soil%22%2C%20%22i%22%29%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%22676982%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%22867468%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%20%22101006717%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%20%29%29%0A%7D
```

**STEP 2. LOAD DOI AND TITLE OF CORDIS PROJECT PUBLICATIONS FROM VIRTUOSO INTO POSTGRES DATABASE SCHEMA 'harvest', ENRICH THE METADATA BY QUERYING OPENAIRE AND LOAD THE RESULT INTO VIRTUOSO**

From the previous step VIRTUOSO holds two triples for every project publication:

* the DOI (as subject, with predicate 'eurio:ProjectPublication' and object the eurio result-URI
* the title (as object, with subject the eurio result-URI and predicate 'dcterms:title')

JAVA project **'soilwise-cordis-fetch-dois'** has runnable class **DBWrite** with method **main** as starting point for all the functionality.

**DBWrite.main** can be invoked in three ways:


* with parameter **'cordis'**
* with parameter **'title'**
* with parameter **'turtle'**

The scheduled CI job 'cordis-harvest' runs them all.

**Step 1** is to invoke **DBWrite** with parameter **'cordis'**.

=\>

DOIs from Cordis Project Publications are queried from Virtuoso, and send to OpenAire.

In case no hit in Openaire: Add the item to table items with:

* identifiertype='cordis'
* resulttype='doi'
* resultobject= the doi value

In case Openaire returns more information on the DOI: Add the item to table items with:

* identifiertype='doi'
* resulttype='oaf'
* resultobject=the JSON Object holding the entire oaf:result

(Querying DOIs from 2598 Project Publications ends up with 2549 hits in OpenAire. And 49 DOIs without data in OpenAire)

**Step 2** is to invoke **DBWrite** with parameter '**title'**.

=\>

Queries all Cordis Project titles from Virtuoso. Result:

* Cordis Projects get added to table 'items', if not already there.

**Step 3** is to invoke **DBWrite** with parameter '**turtle'**.

=\>

For all records with a hit in OpenAire: Convert the oaf:result into Turtle which can be loaded into Virtuoso.

Selection of records:
```
select identifier, resultobject, source from harvest.items where turtle IS NULL and resulttype = 'oaf'
```

When parsing the oaf:result there will be searched for the following predicates:

* creator
  * \-\> dcterms/creator
* collectedfrom
  * \-\> dcterms/isReferencedBy
* bestaccessright
  * \-\> dcterms/license
* description
  * \-\> dcterms/description
* subject
  * \-\> dcterms/subject
* dateofacceptance
  * \-\> dcterms/date
* journal
  * \-\> dcterms/isPartOf
* fulltext **with 'pdf' as part of the string**
  * \-\> dcterms/references (as Literal)
  * \-\> dcat/downloadURL (as URI)


**Step 4** is loading the turtle into Virtuoso. Project **soilwise-repo** has an endpoint to be directly used by Virtuoso load by Resource URL.

The endpoints:

* (test) https://repo.soilwise-he-test.containers.wurnet.nl/item/turtle/CORDIS
* (prod) https://repo.soilwise-he.containers.wur.nl/item/turtle/CORDIS


**Finally the Virtuoso triple store can be used by SPARQL queries**

default-graph-uri <https://soilwise-he.github.io/soil-health>

**Query one doi:**

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX eurio:<http://data.europa.eu/s66#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX datacite: <http://purl.org/spar/datacite/>
select ?sub ?pred ?obj
WHERE {
  ?sub ?pred ?obj
FILTER (?sub= <https://doi.org/10.1002/2017JG004269>) 
}
```

**Query one doi for predicate "isReferencedBy":**

```
PREFIX dcterms:<http://purl.org/dc/terms/>

SELECT ?o
WHERE {
?s ?p ?o
FILTER regex(?p, "isReferencedBy", "i")
FILTER regex(?s,"10.1002/adfm.202112374","i")
}
```


**For a certain DOI query the triple store for the project and project title**
```
PREFIX eurio:<http://data.europa.eu/s66#> 
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
SELECT ?obj ?sub (SELECT ?o WHERE {?s ?p ?o FILTER regex(?p,  "title", "i") FILTER(?s=?sub)} ) 
WHERE {
  ?sub ?pred ?obj
FILTER (?pred=<http://data.europa.eu/s66#hasResult>) 
FILTER (?obj=<https://doi.org/10.1007/s11356-022-22599-4>)
}
```

**Query projects and link all attributes to the title as well (subquery):**
- subQuery the project title
- exclude the project title from being a separate row

```
PREFIX eurio:<http://data.europa.eu/s66#> 
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
SELECT ?sub (SELECT ?o WHERE {?s ?p ?o FILTER regex(?p,  "title", "i") FILTER(?s=?sub)} ) ?pred ?obj
WHERE {
?sub ?pred ?obj 
FILTER regex(?sub,  "cordis.europa.eu/project/id", "i") 
FILTER (!regex(?pred,  "title", "i") )
}
```