# Desc: script updates records table from translations
# Author: Paul van Genuchten
# License: MIT

import os, psycopg2
import sys
sys.path.append('utils')
from database import dbQuery

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

def processRecord(s,t,c):
    myrec = dbQuery("select title,abstract from public.records where identifier=%s or title=%s",(c,s),True)

    for r in myrec:
        title,abstract = r
        if title == s:
            dbQuery(f"update public.records set title=%s  where identifier=%s",(t,c),False)
        elif abstract == s:
            dbQuery(f"update public.records set abstract=%s  where identifier=%s",(t,c),False)
        else:
            print('No match',s)


def main():
    # query database for pending translations
    myrecs = dbQuery("""select source,target,context
                     from harvest.translations 
                     where target is not null""")
    # for each string to be translated, make a request
    for rec in myrecs:
        source,target,context = rec 
        processRecord(source,target,context)
        
    return "OK"

if __name__ == "__main__":
    main()