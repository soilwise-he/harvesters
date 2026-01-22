# Harvesting metadata from ISRIC library

[ISRIC library](https://library.wur.nl/WebQuery/isric) (10250 maps) is a collection of books and maps on global soil maintained by the ISRIC collections team.
There is an overlap with the [EUDASM](https://esdac.jrc.ec.europa.eu/resource-type/national-soil-maps-eudasm) collection (2500 maps). Which makes an interesting case for deduplication.

## fetch.py 

Fetches search results (filtered by 'map') by 50 records per page. For each record a `ris` citation is requested ([sample](https://library.wur.nl/WebQuery/isric/start/2268261)), which includes all metadata properties (including bbox).

## parse.py

The parse script queries the ris metadata from the database and parses the content to Dublin Core metadata, which is placed back into the database (turtle).


