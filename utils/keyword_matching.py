import requests
import json

    
def matchCountryUri(label):
    with open('utils\\country_data.json', 'r') as f:
        uri_labels = json.load(f)
    for uri_label in uri_labels:
        if label.lower() == uri_label['label'].lower():
            return uri_label['uri']
    return None

# def getThesaurus():
#     # sparql query:
#     # select distinct ?country_code ?label 
#     # where 
#     # {?s <http://publications.europa.eu/ontology/euvoc#countryCode> ?country_code.
#     # ?country_code <http://www.w3.org/2004/02/skos/core#prefLabel>?label
#     # filter (lang(?label) = 'en')
#     # }
#     resp = requests.get("https://publications.europa.eu/webapi/rdf/sparql?default-graph-uri=&query=select+distinct+%3Fcountry_code+%3Flabel+%0D%0Awhere+%0D%0A%7B%3Fs+%3Chttp%3A%2F%2Fpublications.europa.eu%2Fontology%2Feuvoc%23countryCode%3E+%3Fcountry_code.%0D%0A%3Fcountry_code+%3Chttp%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23prefLabel%3E%3Flabel%0D%0Afilter+%28lang%28%3Flabel%29+%3D+%27en%27%29%0D%0A%7D%0D%0A%0D%0A%0D%0A%0D%0A&format=application%2Fsparql-results%2Bjson&timeout=0&debug=on&run=+Run+Query+")
#     if resp.ok:
#         res = resp.json()
#         results = res['results']['bindings']
#         uri_labels = []
#         for r in results:
#             uri = r['country_code']['value']
#             label = r['label']['value']
#             uri_labels.append({'uri': uri, 'label':label})
#         return (uri_labels)
#     else:
#         print ('fail to fetch country labels from https://publications.europa.eu')
#         return []


# data = getThesaurus()
# with open('utils\\country_data.json', 'w') as f:
#         json.dump(data, f)



## test
# print(matchCountryUri("China"))

