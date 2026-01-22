

FROM python:3.10.18-slim-bookworm
LABEL maintainer="genuchten@yahoo.com"

RUN apt-get update && apt-get install --yes \
        ca-certificates libexpat1 \
    && rm -rf /var/lib/apt/lists/*

# initially copy only the requirements files
COPY cordis ./cordis
COPY csw ./csw
COPY data.europa.eu ./data.europa.eu
COPY impact4soil ./impact4soil
COPY iso-triplify ./iso-triplify
COPY newsfeeds ./newsfeeds
COPY prepsoil ./prepsoil
COPY record-to-pycsw ./record-to-pycsw
COPY soilmission ./soilmission
COPY utils ./utils

RUN pip install -U pip && \
    python3 -m pip install -r csw/requirements.txt \
    psycopg2-binary && \
    python3 -m pip install -r iso-triplify/requirements.txt && \
    python3 -m pip install -r newsfeeds/requirements.txt && \
    python3 -m pip install -r prepsoil/requirements.txt && \ 
    python3 -m pip install -r record-to-pycsw/requirements.txt && \
    python3 -m pip install -r soilmission/requirements.txt 
