import os
from pygeometa.core import import_metadata

def test_metadata_in_folder():

    directory = os.fsencode('./data/cat-1')
    
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".xml"):
            with open(os.path.join(directory,file),"r") as f:
                print(filename)
                # import from arbitrary schema
                md = import_metadata('autodetect', f.read()) 
                print(md.get('metadata',{}).get('identifier'))
                assert md['metadata']['identifier'] not in [None,'']
                



