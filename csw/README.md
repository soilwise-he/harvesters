# CSW

[CSW](https://www.ogc.org/standard/cat/) can be used to fetch records from:  
- [Bonares data repository](https://www.bonares.de/service-portal/data-repository) ([csw](https://maps.bonares.de/soapServices/services/CSWDiscovery))
- ejpsoil catalogue ([csw](https://catalogue.ejpsoil.eu/csw))
- isric catalogue ([csw](https://data.isric.org/geonetwork/srv/eng/csw))
- islandr project ([csw](https://geonetwork.greendecision.eu/geonetwork/srv/eng/csw))

uses [owslib](https://github.com/geopython/OWSLib) to fetch records

uses [pygeometa mcf](https://github.com/geopython/pygeometa) to capture relevant parts from xml

A harvester run is best configured as a CI-CD pipeline in GIT, using docker image

# environment variables

environment variables can also be added to a .env file

- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- HARVEST_URL
- HARVEST_FILTER


## HARVEST_FILTER syntax

Format json, key-value pairs:

```
export HARVEST_FILTER='{"keywords":"Soil","type":"dataset"}'
```






