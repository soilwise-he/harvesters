# script aims to fetch doi from citation, else delegate to crossref
# crossref approach is inspired by
# https://www.crossref.org/labs/resolving-citations-we-dont-need-no-stinkin-parser/
# license: MIT
# Author: Paul van Genuchten, ISRIC - World Soil Information

import csv
import requests
import urllib.parse
from thefuzz import process

maxrows = 10
table = 'file.csv' # which csv?
column = 1 #in which column are citations?

# todo: grab table/column from params

print("id,doi,citation")

# open table
with open(table, newline='') as csvfile:

    # for line in table
    creader = csv.reader(csvfile, delimiter=',', quotechar='"')
    i = -1
    res = {}
    err = []
    for row in creader:
        i+=1
        if i > 0: # header
            
            if i == maxrows:
                break
            # with citation
            if len(row) > column and row[column] not in [None,'']:
                doi = ''
                cit = row[column]
                if 'doi.org/' in cit:
                    doi = cit.split('doi.org/').pop().strip().split(' ')[0]
                    if doi.endswith('.') or doi.endswith(','):
                        doi = doi[:-1]
                elif 'DOI:' in cit:
                    doi = cit.split('DOI:').pop().strip().split(' ')[0]
                    if doi.endswith('.') or doi.endswith(','):
                        doi = doi[:-1]
                # todo: add check here, to understand if doi starts with '10.'
                else:
                    try:
                        resp =  requests.get(f"https://api.crossref.org/works?rows=1&query.bibliographic={urllib.parse.quote_plus(cit)}")
                        recs = resp.json().get('message',{}).get('items',[])
                        if len(recs) > 0:
                            # since crossref always returns a result, we should understand if the returned record is a full match or a 'guess'
                            
                            ttl = recs[0].get('title',['xxx'])[0].split(',')[0]
                            author = recs[0].get('author',[{}])[0].get('family').split(',')[0]

                            tm = process.extractOne(ttl, cit.split(','))
                            am = process.extractOne(author, cit.split(','))
                            if tm[1] > 65 and am[1] > 65:
                            #if recs[0].get('title',['xxx'])[0] in cit and recs[0].get('author',[{}])[0].get('family') in cit:
                                doi = recs[0].get('DOI','')
                            else:
                                print('No match: ',tm[1],':',ttl,'|',am[1],':'author,'|',cit)
                    except Exception as e:
                        print('error: ',e)

                print(f'{i},{doi},"{cit}"')

                if doi.strip().startswith('10.'):
                    res[doi.strip()] = cit
                else:
                    err.append(cit)
                    
    print('result:',res)
    print('errors:',err)
