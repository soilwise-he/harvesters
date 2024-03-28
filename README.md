# harvesters

a component or approach to fetch metadata (and data?) from remote sources as documented at <https://soilwise-he.github.io/SoilWise-documentation/technical_components/ingestion/>

In this approach each harvester runs in a dedicated container. The result of the harvester is ingested into a (temporary) storage, where follow up processes pick up the results. Typically this process runs as a GITHub actions.

``` mermaid
flowchart LR
    c[CI-CD] -->|task| q[/Queue\]
    r[Runner] --> q
    r -->|deploys| hc[Harvest container]
    hc -->|harvests| db[(temporary storage)]
    hc -->|data cleaning| db[(temporary storage)]
```
