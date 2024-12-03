# Harvesting metadata from ISRIC library

[ISRIC library](https://library.wur.nl/WebQuery/isric) is a collection of books and maps on global soil maintained by the ISRIC collections team.
There is an overlap with the EUDASM collection. Which makes an interesting case for deduplication.

The collection currently holds 10250 maps.

## fetch.py 

Fetches search results (filtered by 'map') by 50 records per page. For each record a `ris` citation is requested, which includes all metadata properties.

## parse.py

The parse script queries the ris metadata from the database and parses the content to Dublin Core metadata, which is placed back into the database (turtle).


