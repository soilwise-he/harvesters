import requests
import extruct
from w3lib.html import get_base_url

url = 'https://data.europa.eu/data/datasets/c52f9599-60de-4bed-ac22-587fc067d6aa?locale=en'
response = requests.get(url)
base_url = get_base_url(response.text, response.url)

data = extruct.extract(response.text, base_url=base_url)
print(data['json-ld'])         # JSON-LD schema.org
print(data['microdata'])       # Microdata items