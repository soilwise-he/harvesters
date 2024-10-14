**QUERY OPENAIRE WITH A DOI TO ENRICH METADATA, LOAD THE RESULT INTO VIRTUOSO TRIPLE STORE .**

Generic component to query OpenAire to retrieve (additional) metadata on a DOI.

The final result will be that for identifiers which are DOIs: 
- the resultype is set to **'oaf' (OpenAire Format)** 
- the resultobject holds the JSON object **oafresult**
- the turtle-field is filled with triples which as-is can be loded into the Virtuoso Triple Store.

**STEPS:** 
- 1. QUERY OPENAIRE
- 2. CREATE TURTLE OUT IF THE RESULT
- 3. LOAD THE TURTLE INTO VIRTUOSO

Both the steps 1 and 2 use the runnable class **DBWrite** from JAVA project **'soilwise-cordis-fetch-dois'**.
The .jar file has originally be created for cordis, and is located inside the cordis folder.
Method **main** from the class **DBWrite**  is the starting point for all the functionality.

For this **DBWrite.main** can be invoked in two ways:

* with parameter **'openairedoi'**
* with parameter **'turtle'**

The scheduled CI job 'openaire-harvest' runs them both.

**Step 1** is to invoke **DBWrite** with parameter **'openaire'**.

=\>

The harvest processes (except CORDIS) store the DOI-values inside the attribute 'identifier' at table 'harvest.items' and set the 'identifiertype' to the value 'doi'.

This leaves this query, to collect the DOIs that have to be enriched:

```
select uri, identifier as doi, source from harvest.items where identifiertype = 'doi' and turtle IS NULL and resulttype != 'oaf';
```

Only take into account records where turtle is NULL and the resultype is not 'oaf'.


```
https://api.openaire.eu/search/researchProducts?format=json&doi=<doi>
```

In case there is a hit and Openaire returns more information on the DOI: Update the item inside table items:

* resulttype='oaf'
* resultobject=the JSON Object holding the entire oaf:result


**Step 2** is to invoke **DBWrite** with parameter '**turtle'**.

=\>

For all records with a hit in OpenAire: Convert the oaf:result into Turtle which can be loaded into Virtuoso.

When parsing the oaf:result there will be searched for the following predicates:

* "creator"
  * \-\> dcterms/creator
* collectedfrom
  * \-\> dcterms/isReferencedBy
* bestaccessright
  * \-\> dcterms/license
* description
  * \-\> dcterms/description
* subject
  * \-\> dcterms/subject
* journal
  * \-\> dcterms/isPartOf


**Step 3** is loading the turtle into Virtuoso. Project **soilwise-repo** has an endpoint to be directly used by Virtuoso load by Resource URL.
The Turtle can be accessed by SOURCE:

The endpoints:

* (test) https://repo.soilwise-he-test.containers.wurnet.nl/item/turtle/IMPACT4SOIL?pageNo=0 / 1 / 2 etc. 
* (prod) https://repo.soilwise-he.containers.wur.nl/item/turtle/IMPACT4SOIL?pageNo=0 / 1 / 2 etc.

**As the TURTLE result can exceed the limits set by Virtuoso paging has been implemented. The default pageSize=3000**


**Finally the Virtuoso triple store can be used by SPARQL queries**

default-graph-uri <https://soilwise-he.github.io/soil-health>

**Query one doi:**

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX datacite: <http://purl.org/spar/datacite/>
select ?sub ?pred ?obj
WHERE {
  ?sub ?pred ?obj
FILTER (?sub= <https://doi.org/10.5061/dryad.xpnvx0kd8>) 
}
```

**Query one doi for predicate "isReferencedBy":**

```
PREFIX dcterms:<http://purl.org/dc/terms/>

SELECT ?o
WHERE {
?s ?p ?o
FILTER regex(?p, "isReferencedBy", "i")
FILTER regex(?s,"10.5061/dryad.xpnvx0kd8","i")
}
```

