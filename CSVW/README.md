# CSVW

[CSVW](https://www.csvw.org) is a standardised protocol to describe CSV's as a knowledge graph, 
the graph is expected to include records in DCAT or schema.org format

The harvester uses csvwlib to parse the csv as knowledge graph

```
pip3 install -r CSVW/requirements.txt
python3 CSVW/import.py
```