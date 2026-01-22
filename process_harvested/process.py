"""
Script: pygeometa_harmonize_to_postgres.py

Purpose:
- Read rows from a Postgres table containing a BLOB/bytea field with metadata in various schemas.
- Use pygeometa to detect schema and harmonize to a common model (MCF-like dict).
- Store harmonized metadata in relational tables under a configurable schema (default: 'metadata').
- Only process source rows whose content MD5 hash has not been processed before.

Notes:
- Requirements:
    pip install sqlalchemy psycopg2-binary python-dotenv pygeometa

Usage:
    export DATABASE_URL=postgresql://user:pass@host:5432/dbname
    export TARGET_SCHEMA=metadata  # optional
    python pygeometa_harmonize_to_postgres.py

"""

import os
import sys
import json
import base64
import logging
from typing import Dict, Any, Tuple
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, UniqueConstraint, MetaData, text as sql_text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv

# load .env if present
load_dotenv()

# Logger configuration to stdout
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

DATABASE_URL = os.getenv('DATABASE_URL')
SOURCE_TABLE = os.getenv('SOURCE_TABLE', 'source_metadata')
BLOB_FIELD = os.getenv('BLOB_FIELD', 'payload')
ID_FIELD = os.getenv('ID_FIELD', 'id')
MD5_FIELD = os.getenv('MD5_FIELD', 'content_md5')
TARGET_SCHEMA = os.getenv('TARGET_SCHEMA', 'metadata')

if not DATABASE_URL:
    logger.error('Please set DATABASE_URL environment variable (postgres connection string).')
    sys.exit(1)

# Initialize schema metadata dynamically
schema_metadata = MetaData(schema=TARGET_SCHEMA)
Base = declarative_base(metadata=schema_metadata)

class Contact(Base):
    __tablename__ = 'contacts'
    __table_args__ = {'schema': TARGET_SCHEMA}

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    email = Column(String)
    phone = Column(String)
    position = Column(String)
    organization = Column(String)
    address = Column(Text)
    town = Column(String)
    country = Column(String)
    url = Column(String)

    contact_links = relationship('ContactMetadata', back_populates='contact', cascade='all, delete-orphan')

class Record(Base):
    __tablename__ = 'records'
    __table_args__ = {'schema': TARGET_SCHEMA}

    id = Column(Integer, primary_key=True)
    source_id = Column(String, unique=True, nullable=True)
    source_md5 = Column(String, unique=True, nullable=True)
    title = Column(String)
    abstract = Column(Text)
    raw_mcf = Column(Text)

    contact_links = relationship('ContactMetadata', back_populates='record', cascade='all, delete-orphan')
    distributions = relationship('Distribution', cascade='all, delete-orphan')

class ContactMetadata(Base):
    __tablename__ = 'contact_metadata'
    __table_args__ = (
        UniqueConstraint('contact_id', 'record_id', 'role', name='uix_contact_metadata_role'),
        {'schema': TARGET_SCHEMA}
    )

    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey(f'{TARGET_SCHEMA}.contacts.id', ondelete='CASCADE'), nullable=False)
    record_id = Column(Integer, ForeignKey(f'{TARGET_SCHEMA}.records.id', ondelete='CASCADE'), nullable=False)
    role = Column(String, nullable=True)

    contact = relationship('Contact', back_populates='contact_links')
    record = relationship('Record', back_populates='contact_links')

class Distribution(Base):
    __tablename__ = 'distributions'
    __table_args__ = {'schema': TARGET_SCHEMA}

    id = Column(Integer, primary_key=True)
    record_id = Column(Integer, ForeignKey(f'{TARGET_SCHEMA}.records.id', ondelete='CASCADE'))
    format = Column(String)
    url = Column(String)
    details = Column(Text)

engine = None
if DATABASE_URL.split(':')[0]=='sqlite':
    engine = create_engine(DATABASE_URL, connect_args={"autocommit": False})
elif DATABASE_URL.split(':')[0]=='postgresql':
    engine = create_engine(DATABASE_URL,connect_args={'sslmode':'require'},echo=True)

Session = sessionmaker(bind=engine)

def ensure_schema_exists(engine, schema_name: str):
    with engine.begin() as conn:  # use begin() for transaction context
        conn.execute(sql_text(f'CREATE SCHEMA IF NOT EXISTS {schema_name}'))

def create_schema():
    ensure_schema_exists(engine, TARGET_SCHEMA)
    Base.metadata.create_all(engine, checkfirst=True)

def convert_to_mcf_using_pygeometa(text: str) -> Dict[str, Any]:
    try:
        from pygeometa.core import import_metadata
        md = import_metadata('autodetect', text)
        return md
    except Exception as e:
        logger.exception('Failed to parse metadata with pygeometa.import_metadata: %s', e)
        raise

def get_or_create_contact(session, contact_obj):
    name = None
    email = None
    phone = None
    position = None
    organization = None
    address = None
    town = None
    country = None
    url = None

    if isinstance(contact_obj, str):
        name = contact_obj
    elif isinstance(contact_obj, dict):
        name = contact_obj.get('organisationName') or contact_obj.get('name') or contact_obj.get('org')
        email = contact_obj.get('email') or contact_obj.get('electronicMailAddress')
        phone = contact_obj.get('phone') or contact_obj.get('telephone')
        position = contact_obj.get('positionName') or contact_obj.get('position')
        organization = contact_obj.get('organisationName') or contact_obj.get('organization')
        address = contact_obj.get('deliveryPoint') or contact_obj.get('address')
        town = contact_obj.get('city') or contact_obj.get('town')
        country = contact_obj.get('country')
        url = contact_obj.get('onlineResource') or contact_obj.get('url')
        if not name:
            try:
                name = contact_obj.get('CI_ResponsibleParty', {}).get('organisationName')
            except Exception:
                name = None
    if not name:
        name = 'unknown'

    existing = session.query(Contact).filter(Contact.name == name).first()
    if existing:
        for field, value in {
            'email': email,
            'phone': phone,
            'position': position,
            'organization': organization,
            'address': address,
            'town': town,
            'country': country,
            'url': url,
        }.items():
            if value and not getattr(existing, field):
                setattr(existing, field, value)
        session.add(existing)
        session.flush()
        return existing

    c = Contact(
        name=name,
        email=email,
        phone=phone,
        position=position,
        organization=organization,
        address=address,
        town=town,
        country=country,
        url=url,
    )
    session.add(c)
    session.flush()
    return c

def insert_record(session, source_id: str, source_md5: str, mcf: Dict[str, Any]):
    id = mcf.get('identification',{}) or {}
    md = mcf.get('metadata',{}) or {}
    dt = mcf.get('distribution',{}) or {}
    ct = mcf.get('contacts',{}) or {}
    record = Record(
        source_id=source_id,
        source_md5=source_md5,
        title=id.get('title',''),
        abstract=id.get('abstract',''),
        raw_mcf=json.dumps(mcf, default=str)
    )
    session.add(record)
    session.flush()

    for k,c in ct.items():
        contact_obj = c
        role = c.get('role') or k

        try:
            contact_ref = get_or_create_contact(session, contact_obj)
            link = session.query(ContactMetadata).filter_by(contact_id=contact_ref.id, record_id=record.id, role=role).first()
            if not link:
                link = ContactMetadata(contact_id=contact_ref.id, record_id=record.id, role=role)
                session.add(link)
        except Exception:
            logger.exception('Failed creating contact/link for record %s', source_id)

    for k,d in dt.items():
        url = d.get('url') if isinstance(d, dict) else None
        fmt = d.get('type') if isinstance(d, dict) else None
        details = json.dumps(d, default=str) if isinstance(d, (dict, list)) else str(d)
        dist = Distribution(record_id=record.id, format=fmt, url=url, details=details)
        session.add(dist)

    session.flush()
    return record

def process_all_source_rows():
    conn = engine.connect()
    trans = conn.begin()
    try:
        rs = conn.execute(f'SELECT identifier, resultobject, hash, turtle FROM {SOURCE_TABLE} LIMIT 20')
        rows = rs.fetchall()
        logger.info('Read %d rows from source table %s', len(rows), SOURCE_TABLE)
        session = Session()
        for r in rows:
            try:
                source_id = str(r[0])
                text = r[1]
                source_md5 = str(r[2]) if r[2] is not None else None # is already parsed? move to initial 

                if source_md5:
                    existing = session.query(Record).filter(Record.source_md5 == source_md5).first()
                    if existing:
                        logger.info('Skipping source id %s (md5 already processed)', source_id)
                        continue

                logger.info('parsing %s', source_id)
                mcf = convert_to_mcf_using_pygeometa(text)
                if not mcf and r[3] != '': # try turtle field
                   mcf = convert_to_mcf_using_pygeometa(r[3]) 
        
                if mcf:    
                    insert_record(session, source_id, source_md5, mcf)
                    session.commit()
                    logger.info('Inserted record for source id %s', source_id)
                else:
                    logger.exception('No record %s', r[0],text)
            except Exception:
                session.rollback()
                logger.exception('Error processing source record %s', r[0])
        session.close()
        trans.commit()
    except Exception:
        trans.rollback()
        logger.exception('Error reading source table')

if __name__ == '__main__':
    create_schema()
    process_all_source_rows()
    logger.info('Done.')
