# ISO Triplify

For any iso19139:2007 records, this metadata transformation utility can be used to transform the iso to rdf.
It uses a modified version of the [semic-eu iso2dcat](https://github.com/SEMICeu/iso-19139-to-dcat-ap) xslt.

The resulting DCAT RDF is serialised as turtle and stored in the `turtle` column of the harvest.items table.

Run this transform utility as a gitlab-ci pipeline, from the [CI](../CI) folder.