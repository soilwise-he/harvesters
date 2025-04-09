

FROM python:3.8-slim-buster
LABEL maintainer="genuchten@yahoo.com"

RUN apt-get update && apt-get install --yes \
        ca-certificates libexpat1 \
    && rm -rf /var/lib/apt/lists/*

# initially copy only the requirements files
COPY csw ./csw
COPY esdac ./esdac
COPY impact4soil ./impact4soil
COPY iso-triplify ./iso-triplify
COPY prepsoil ./prepsoil
COPY record-to-pycsw ./record-to-pycsw
COPY translate ./translate
COPY newsfeeds ./newsfeeds
COPY utils ./utils

RUN pip install -U pip && \
    python3 -m pip install \
    -r csw/requirements.txt \
    psycopg2-binary && \
    python3 -m pip install \
    -r esdac/requirements.txt && \
    python3 -m pip install \
    -r iso-triplify/requirements.txt && \
    python3 -m pip install \
    -r record-to-pycsw/requirements.txt && \
    python3 -m pip install \
    -r newsfeeds/requirements.txt   


