# ipchem database

[IPCHEM](ipchem.jrc.ec.europa.eu) - the Information Platform for Chemical Monitoring is the European Commission’s reference access point for searching, accessing and retrieving chemical occurrence data collected and managed in Europe. The platform has been developed to fill the knowledge gap on chemical exposure and its burden on health and the environment. 

**The IPCHEM API is protected with a [CSRF token](https://en.wikipedia.org/wiki/Cross-site_request_forgery), which makes interaction with the API difficult. The work is paused for that reason.**

## Harvesting ipchem data

ipchem provides an api to retrieve dataset metadata, the model is [oriented on dublin core](https://www.sciencedirect.com/science/article/pii/S1438463919310752?via%3Dihub)

## API

POST [retrieveDataset](https://ipchem.jrc.ec.europa.eu/ipchem-data-access-p/RetrieveDataset) 
    - SORT: 'Data+Collection+Acronym'+ASC
    - PAGE_NUMBER: 1
    - PAGE_SIZE: 100
    - MEDIA: Soil+(Topsoil);Soil+(Subsoil)

POST [getMetadata](https://ipchem.jrc.ec.europa.eu/ipchem-data-access-p/GetMetadata)
    - DATASET: BIOSOIL

