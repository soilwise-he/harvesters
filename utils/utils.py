# various metadata utils
import hashlib,json

def to_schema_org(r, mapping=None):
    if mapping is None:
        mapping =  {
            'abstract': 'description',
            'id': 'identifier',
            'publication_date': 'datePublished',
            'authors': 'creator',
            'author': 'creator',
            'issued': 'datePublished',
            'created': 'dateCreated',
            'modified': 'dateModified',
            'subject': 'about'
        }
    for k,v in mapping.items():
        if k in r:
            # if target field exists, append or extend 
            if v in r and r[v] not in [None,'']:
                if isinstance(r[v], list):
                    if isinstance(r[k], list):
                        r[v].extend(r[k])
                    elif r[k] not in [None,'']:
                        r[v].append(r[k])
                else:
                    if isinstance(r[k], list):
                        r[v] = [r[v]] + r[k]
                    elif r[k] not in [None,'']:
                        r[v] = [r[v], r[k]]
            else:
                r[v] = r.pop(k) 
    if not '@context' in r:
        r['@context'] = "https://schema.org"
    if not '@type' in r:
        r['@type'] = 'CreativeWork'
    if 'url' in r and r['url'] not in [None,'']:
        firsturl = r['url']
        if isinstance(r['url'], list) and len(r['url'])>0:
            firsturl = r['url'][0]
        if firsturl.startswith('http'):
            r['identifier'] = firsturl

    r['identifier'] = doi_from_url(r.get('identifier',hashlib.md5(json.dumps(r).encode("utf-8")).hexdigest()))

    return r

def doi_from_url(uri):
    try:
        if 'doi.org' in uri:
            return uri.split('?')[0].split('doi.org/').pop().strip()
        elif 'zenodo.org' in uri:
            parts = uri.split('?')[0].split('/')
            if 'record' in parts:
                idx = parts.index('record')
                if idx + 1 < len(parts):
                    return '10.5281/zenodo.' + parts[idx + 1]
        elif 'doi:' in uri:
            return uri.split('doi:').pop().strip()
        elif 'figshare.com' in uri:
            # remove querystring
            parts = uri('?')[0].split('/')
            if 'articles' in parts:
                idx = parts.index('articles')
                if idx + 2 < len(parts):
                    return '10.6084/m9.figshare.' + parts[idx + 2]
        elif 'datadryad.org' in uri: # should not get here, should be matched by doi: (https://datadryad.org/dataset/doi:10.5061/dryad.qfttdz0qv)
            parts = uri('?')[0].split('/')
            if 'dataset' in parts:
                idx = parts.index('dataset')
                if idx + 1 < len(parts):
                    return '10.5061/dryad.' + parts[idx + 1]
    except Exception:
        None
    return uri

def pid_type(id):
    if id.startswith('10.') and len(id.split('/')) > 1:
        return 'doi'
    elif id.startswith('http'):
        return 'uri'
    else:
        return 'uuid'
