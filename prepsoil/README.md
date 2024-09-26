# Impact4soil harvest

[prepsoil](https://cordis.europa.eu/project/id/101070045) is a HE funded project creating a knowledge hub with data, knowledge and living labs in preparation for the soil deal for Europe

## Harvesters

- knowledge
- living labs / lighhouses

prepsoil has a minimal metadata profile, and forwards users to remote locations, unfortunately hardly any usage of DOI. 

## Operation

```cmd
cd harvesters
virtualenv .
. bin/activate
pip install -r prepsoil/requirements.txt
python prepsoil/fetch.py
python prepsoil/parse.py
```
