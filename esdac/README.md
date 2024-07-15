# Harvesting metadata from ESDAC

[ESDAC](https://esdac.jrc.ec.europa.eu) is a drupal website with dedicated sections for datasets, maps and documents. This folder contains 2 scripts which together bring the esdac records into SWR.

## fetch.py 

Fetches the html pages into the postgres database.

- For datasets, first 5 list pages are collected, from each listing, the relevant page links are scraped. 
Then each link is fetched. 
- For maps (EUDASM) and documents, there are no child pages, so the metadata is directly scraped from the list page

## parse.py

The parse script queries the html from the database and parses the content to Dublin Core metadata, which is placed back into the database.

