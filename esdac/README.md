# Harvesting metadata from ESDAC

[ESDAC](https://esdac.jrc.ec.europa.eu) is a drupal website with dedicated sections for datasets, maps and documents. This folder contains 2 scripts which together bring the esdac records into SWR.

## fetch.py 

Fetches the html pages into the postgres database.

- For datasets, first 5 list pages are collected, from each listing, the relevant page links are scraped. 
Then each link is fetched. 
- For maps (EUDASM) and documents, there are no child pages, so the metadata is directly scraped from the list page

## fetch-projects.py

Fetches the relevant projects from 
- https://esdac.jrc.ec.europa.eu/projects/Eufunded/Eufunded.html
- https://mission-soil-platform.ec.europa.eu/project-hub/funded-projects-under-mission-soil

Which are later used as a filter to query openaire

## parse.py

The parse script queries the html from the database and parses the content to Dublin Core metadata, which is placed back into the database.

## Resume parameter

The harvest process should resume where it left of last time. This mechanism is triggered by a environment parameter `HV_RESUME` (default:true). Url's requested in previous runs are fetched from database and each url to be requested is verified if it exists in this list.

