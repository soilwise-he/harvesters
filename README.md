# SWR Harvesters

A component to fetch metadata from remote sources as documented at <https://soilwise-he.github.io/SoilWise-documentation/technical_components/ingestion/>.

Harvesting tasks can best be triggered from a tast runner, such as a CI-CD pipeline. Configuration scripts for running various harvesting tasks in a Gitlab CI-CD environment are available in [CI](./CI/). Tasks are configured using environment variables. The result of the harvester are ingested into a PostGres storage, where follow up processes pick up the results.

``` mermaid
flowchart LR
    c[CI-CD] -->|task| q[/Queue\]
    r[Runner] --> q
    r -->|deploys| hc[Harvest container]
    hc -->|harvests| db[(temporary storage)]
    hc -->|data cleaning| db[(storage)]
    db -->|triplify| TS[(Triple store)]
    db -->|indexing| CT[Catalogue] 
```

This component is tightly related to the [triple store](https://github.com/soilwise-he/triplestore-virtuoso) component and [catalogue component](https://github.com/soilwise-he/pycsw). Harvested records are stored on the triple store as well as the catalogue storage. 

The following harvesting tasks are available.

## Fetch records 

- [CSW](./csw) (for example Bonares, EJP Soil, islandr, inspire)
- [ESDAC](./esdac) a dedicated API
- [Cordis/OpenAire](./cordis) combination of SPARQL and API's
- [Prepsoil](./prepsoil/) a dedicated API
- [Newsfeeds](./newsfeeds/) imports newsfeeds from soil mission websites

## Process records

- [iso-triplify](./iso-triplify/) exports iso19139 records to GeoDCAT-AP to be included in SWR triplestore
- [record-to-pycsw](./record-to-pycsw/) exports records to catalogue (as iso19139 or Dublin Core)
- [translate](./translate/) triggers a translation of non english records

## Docker

Run script as docker.
Create a .env file with harvester details.

```
docker build -t soilwise/harvesters .
docker run --env-file csw/.env soilwise/harvesters python csw/metadata.py 
```