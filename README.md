# harvesters

- Component: Harvested
- Lead: Paul & Cenk

A component or approach to fetch metadata (and data?) from remote sources as documented at <https://soilwise-he.github.io/SoilWise-documentation/technical_components/ingestion/>

In this approach each harvester runs in a dedicated container. The result of the harvester is ingested into a (temporary) storage, where follow up processes pick up the results. Typically this process runs as a GITHub actions.

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

This repository will contain the definition of a container used as a github action to harvest resources; as well as git action definitions to harvest actual sources. 

This component is tightly related to the [triple store](https://github.com/soilwise-he/triplestore-virtuoso) component. Harvested records are stored on the triple store. Some interaction with the triple store to understand if existing records need to be kept, overwritten or even removed. 

## Harvesters

- [inspire](./inspire)
- [CSW](./csw) (for example Bonares, EJP Soil)
- [ESDAC](./esdac)
- [Cordis/OpenAire](./cordis)
- [Triplify](./mcf-triplify/)

## Docker

Run script as docker

```
docker built -t soilwise/harvesters .
docker run -e POSTGRES_HOST=localhost soilwise/harvesters python wcs/metadata.py 
```