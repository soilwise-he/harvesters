# INSPIRE Geoportal

Filters: 
- INSPIRE theme: Soil
- Spatial scope: National (Italy, Germany and Belgium are regionally oriented, without this filter there are 600 results, now 60)

The geoportal in theory supports CSW, unfortunately we haven't been able to get it to work, see [issue](https://github.com/INSPIRE-MIF/helpdesk-geoportal/issues/195). For that reason we query the GeoNetwork API directly, which is a proxy to the underlying Elastic Search API. We use `pycurl`, because with `requests`, the API did not return usefull responses.

We use the [pygeometa](https://github.com/geopython/pygeometa) library to capture a subset of iso documents.

Documents are identified using their md5 hash, so the database also builds up a history in case records change over time.

Records which fail parsing are not processed further.





