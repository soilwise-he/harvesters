# CSW

Catalogue service for the web [CSW](https://www.ogc.org/standard/cat/) is a standardised protocol to query remote catalogues.

This library can be used to fetch records from CSW servers. 

Some relevant CSW catalogues are:

- [Bonares data repository](https://www.bonares.de/service-portal/data-repository) ([csw](https://maps.bonares.de/soapServices/services/CSWDiscovery))
- ejpsoil catalogue ([csw](https://catalogue.ejpsoil.eu/csw))
- isric catalogue ([csw](https://data.isric.org/geonetwork/srv/eng/csw))
- islandr project ([csw](https://geonetwork.greendecision.eu/geonetwork/srv/eng/csw))

The script uses the [owslib](https://github.com/geopython/OWSLib) library to fetch records and stores them on a PostGreSQL database table `harvest.items` with structure

```sql
CREATE TABLE IF NOT EXISTS harvest.items
(
    identifier text COLLATE pg_catalog."default" NOT NULL,
    identifiertype character varying(50) COLLATE pg_catalog."default",
    itemtype character varying(50) COLLATE pg_catalog."default",
    resultobject text COLLATE pg_catalog."default" NOT NULL,
    resulttype character varying(50) COLLATE pg_catalog."default",
    uri text COLLATE pg_catalog."default" NOT NULL,
    insert_date timestamp without time zone,
    source text COLLATE pg_catalog."default",
    hash text COLLATE pg_catalog."default",
    turtle text COLLATE pg_catalog."default",
    date character varying(10) COLLATE pg_catalog."default",
    error text COLLATE pg_catalog."default",
    language character varying(9) COLLATE pg_catalog."default",
    project text COLLATE pg_catalog."default",
    CONSTRAINT item_pkey PRIMARY KEY (identifier),
    CONSTRAINT item_hash UNIQUE (hash)

```

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






