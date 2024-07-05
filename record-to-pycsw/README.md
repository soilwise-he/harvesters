# Record to pycsw

At this moment it seems most feasible to export the ingested metadata records in a pycsw format, so no changes are needed to pycsw.

The challenge is that we currently don't pre process the records, pycsw will not benefit from metadata augmentation

In a later stage we have 3 options:
- Augmented metadata is stored in triple store; a sparql query extracts the relevant info for pycsw
- Augmented metadata is formatted to match the pycsw model
- pycsw (or a tailored UI) is finetuned so it interacts directly with the augmented metadata

The script is based on the [pycsw-admin script](https://github.com/geopython/pycsw/blob/master/pycsw/core/admin.py), in stead of reading files, it takes results from a database.



