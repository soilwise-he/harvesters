# Desc: script triggers translation for prepared keys
# Author: Paul van Genuchten
# License: MIT

import requests, json, os  
from dotenv import load_dotenv
import psycopg2
from requests.auth import HTTPDigestAuth
from datetime import datetime, timedelta

import sys
sys.path.append('utils')
from database import dbQuery, insertSQL

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

eTranslationRestUrl = os.environ.get("TR_SERVICE_URL") or "https://webgate.ec.europa.eu/etranslation/si/translate"
applicationName = os.environ.get("TR_LOGIN") or 'Soilwise-he'
password = os.environ.get("TR_PASSCODE")
callbackUrl = os.environ.get("TR_CALLBACK_URL")

allowed_languages = os.environ.get("TR_ALLOWED_LANGUAGES") or '*'

def requestRecord(lang_source,lang_target,source):

    if lang_source in [None,'']:
        lang_source = 'LD' # Language Detection

    translationRequest = {}
    translationRequest['sourceLanguage'] = lang_source
    translationRequest['targetLanguages'] = [lang_target]
    translationRequest['callerInformation'] = {"application" : applicationName, "username":"ingest-bot"}
    translationRequest['textToTranslate'] = source
    translationRequest['requesterCallback'] = callbackUrl

    jsonTranslationRequest = json.dumps(translationRequest)
    jsonHeader = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    requestId = None

    try:
        response = requests.post(eTranslationRestUrl, auth=HTTPDigestAuth(applicationName, password), headers = jsonHeader, data=jsonTranslationRequest)  
        response.raise_for_status()
        requestId = response.text
    except requests.exceptions.HTTPError as err:
        print(err)
        
    print(response.text)

    if(requestId and requestId not in [None,'']):
        # insert the ticket to the database, to identify which string to be updated
        dbQuery("update harvest.translations set ticket=%s where lang_target=%s and source=%s;",(requestId,lang_target,source),hasoutput=False)
        return requestId
    else:
        return "Error: No requestId"
    
def main():
    # query database for pending translations
    myrecs = dbQuery("""select source,lang_source,lang_target 
                     from harvest.translations 
                     where target is null
                     and (ticket is null or date_inserted < now() - interval '1 day')""")
    # for each string to be translated, make a request
    for rec in myrecs:
        source,lang_source,lang_target = rec 
        requestRecord(lang_source,lang_target,source)
        
    return "OK"

if __name__ == "__main__":
    main()