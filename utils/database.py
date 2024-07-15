import json, os, psycopg2
from datetime import datetime


def dbInit():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT"),
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD")
    )  

def dbQuery(sql,params=(),hasoutput=True):
    dbconn = dbInit()
    try:
        cursor = dbconn.cursor()
        cursor.execute(sql,params)
        if hasoutput:
            return cursor.fetchall()
        else:
            dbconn.commit()
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        dbconn.close();


def insertRecord(identifier,resulttype,resultobject,hashcode,source,title="",description="",date="",itemtype="",uri="",identifiertype=""):

    # todo: check existing before enter?
    insertSQL('harvest.items',['identifier','identifiertype','uri','resultobject','resulttype','hash',  'source','insert_date','itemtype','title','description','date'],
                                (identifier,   identifiertype,  uri,  resultobject,  resulttype,  hashcode,source, datetime.now(),itemtype,title,description,date)) # insert into db
    
    # add for duplicate check
    insertSQL('harvest.item_duplicates',['identifier','identifiertype','source','hash'],(identifier,identifiertype,source,hashcode))


def insertSQL(table, fields, values):
    
    sql = f"INSERT INTO {table} ({', '.join(fields)}) values ({','.join(['%s' for x in range(len(fields))])}) ON CONFLICT DO NOTHING;"

    dbconn = dbInit()
    with dbconn.cursor() as cur:
        try:
            # execute the INSERT statement
            cur.execute(sql, values)
            # commit the changes to the database
            dbconn.commit()
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            dbconn.close();
      

