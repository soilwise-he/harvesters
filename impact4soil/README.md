# Impact4soil harvest

The [Impact4Soil platform](https://www.impact4soil.com/) is here to drive cooperation and knowledge sharing on soil carbon at an international level.

## Harvesters

- datasets
- documents

Impact4soil has a minimal metadata profile, but registers resources preferably by DOI. 
Harvested records are imported as a DOI. The DOI OpenAire harvester then takes over to load additional metadata from OpenAire.

## Operation

```cmd
cd harvesters
virtualenv .
. bin/activate
pip install -r impact4soil/requirements.txt
python impact4soil/metadata.py
```
