# CSW

Catalogue service for the web [CSW](https://www.ogc.org/standard/cat/) is a standardised protocol to query remote catalogues.

This library can be used to fetch records from CSW servers. 

Some relevant CSW catalogues are:

- [Bonares data repository](https://www.bonares.de/service-portal/data-repository) ([csw](https://maps.bonares.de/soapServices/services/CSWDiscovery))
- ejpsoil catalogue ([csw](https://catalogue.ejpsoil.eu/csw))
- isric catalogue ([csw](https://data.isric.org/geonetwork/srv/eng/csw))
- islandr project ([csw](https://geonetwork.greendecision.eu/geonetwork/srv/eng/csw))
- FAO
- EEA
- [INSPIRE geoportal](https://inspire-geoportal.ec.europa.eu/srv/eng/csw)

The script uses the [owslib](https://github.com/geopython/OWSLib) library to fetch records and stores them on a PostGreSQL database table `harvest.items` with structure

A harvester run is best configured as a CI-CD pipeline in GIT. You can run this harvest locally by adding a .env file in this folder, from parent folder run:

```
pip3 install -r csw/requirements.txt
python3 csw/metadata.py
```

## Environment variables

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

for INSPIRE Soil theme
```
HARVEST_FILTER=[{"th_httpinspireeceuropaeutheme-theme.link":"http://inspire.ec.europa.eu/theme/so"}] 
```





