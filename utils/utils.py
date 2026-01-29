# various metadata utils
import hashlib,json

def to_schema_org(r, mapping=None):
    if mapping is None:
        mapping =  {
            'title': 'name',
            'abstract': 'description',
            'id': 'identifier',
            'published': 'datePublished',
            'authors': 'creator',
            'author': 'creator',
            'issued': 'datePublished',
            'created': 'dateCreated',
            'modified': 'dateModified',
            'subject': 'keywords'
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
    r['identifier'] = doi_from_url(r.get('identifier', 
                                    r.get('@id', 
                                     r.get('url',
                                      hashlib.md5(json.dumps(r).encode("utf-8")).hexdigest()))), 
                                    r.get('@id', r.get('url','')))
    if '@id' not in r:
        r['@id'] = r.get('url',r.get('identifier'))

    return r

def doi_from_url(uri, uri2=""):
    # prefer doi urls
    if not isinstance(uri2, list):
        uri2 = [uri2]
    for u in uri2:
        selected = ['doi.org','doi:','zenodo.org','data.jrc.ec.europa.eu','figshare.com','datadryad.org','/geonetwork']
        for s in selected:
            if s in u:
                uri = u
                break
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
        elif 'data.jrc.ec.europa.eu' in uri:
            return uri.split('?')[0].split('/').pop().strip()
        elif '/geonetwork' in uri:
            return uri.split('?')[0].split('/').pop().strip()
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

def pid_type(id1, resolve=False):
    if id1.startswith('10.') and len(id1.split('/')) > 1 and len(id1.split('/')[0].split('.')) == 2:
        if resolve: # could try a resolve of the doi... slow...
            None
        return 'doi'
    elif id1.startswith('http'):
        return 'uri'
    else:
        return 'uuid'
