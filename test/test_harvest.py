import os, copy
import pytest
import sys
sys.path.append('utils')
from pygeometa.core import import_metadata
from utils import doi_from_url, pid_type, to_schema_org

def test_doi_extraction():
    assert doi_from_url('http://doi.org/lala', ['la','','http://foo']) == 'lala'
    assert doi_from_url('foo', ['la','','http://foo']) == 'foo' 
    assert doi_from_url('foo', ['la','','http://doi.org/lala']) == 'lala'
    assert doi_from_url('foo', 'http://doi.org/lala') == 'lala'

def test_schema_org():
    r = {'title': 'zozo', 'abstract': 'hoe la', 'url': 'https://example.com'}
    rp = to_schema_org(copy.deepcopy(r)) #no mapping, use copy to preserve original dict
    assert rp['name'] == 'zozo'
    assert rp['description'] == 'hoe la'
    assert rp['@id'] == 'https://example.com'
    m = {'title': 'description'} # title field is mapped to description field
    rp = to_schema_org(copy.deepcopy(r) , m) # with mapping
    assert rp['description'] == 'zozo'
    assert rp['abstract'] == 'hoe la'
    assert 'title' not in rp
    m = {'description': 'description'} # should keep description
    r = {'description': 'hoe la', 'name':'foo'}
    rp = to_schema_org(r , m) # with mapping
    assert rp['description'] == 'hoe la'
def test_pid_type():
    assert pid_type('lala') == 'uuid'
    assert pid_type('10.100/rty') == 'doi'
    assert pid_type('10.10.10.100/rty/foo/la') == 'uuid'
    assert pid_type('http://foo') == 'uri'
    assert pid_type('http://foo.com/hoo/boo?we=now#optimal-care') == 'uri'

def test_metadata_in_folder():
    for dir in ['test/data/cat-1','test/data/cat-2']:
        for file in os.listdir(dir):
            filename = os.fsdecode(file)
            if not filename.endswith(".tmp"):
                with open(os.path.join(dir,file),"r") as f:
                    # import from arbitrary schema
                    md = import_metadata('autodetect', f.read()) 
                    assert md, f"Failed parsing on '{filename}'"
                    assert md.get('metadata',{}).get('identifier') not in [None,''], f"No identifier on '{filename}', md.keys: {md.get('metadata',{}).keys()}"




