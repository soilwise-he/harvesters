import json,os, psycopg2


def insertRecord(rec, hashcode, source):

    sql = """INSERT INTO doi.publications(
	identifier, oafresult, uri, insert_date, title, description, subject, creator, publisher, contributor, source, license, hash, type)
	VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

    dbconn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT"),
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD")
    )

    with dbconn.cursor() as cur:
        try:
            # execute the INSERT statement
            md = rec.get('metadata',{})
            ident = rec.get('identification',{})
            ct = rec.get('contact',{})
            cur.execute(sql, (  md.get('identifier',''), 
                                json.dumps(md), 
                                md.get('dataseturi',''), 
                                md.get('datestamp',''), 
                                ident.get('title',''), 
                                ident.get('abstract',''), 
                                ";".join(ident.get('keywords',{}).get('default',{}).get('keywords',[])), 
                                ct.get('pointOfContact',{}).get('organization',''),
                                ct.get('distributor',{}).get('organization',''),
                                ct.get('contributor',{}).get('organization',''), 
                                source, 
                                ident.get('license',{}).get('url',ident.get('license',{}).get('name','')), 
                                hashcode,
                                md.get('hierarchylevel','') ))
            # commit the changes to the database
            dbconn.commit()
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            dbconn.close();
      

