

FROM python:3.8-slim-buster
LABEL maintainer="genuchten@yahoo.com"

RUN apt-get update && apt-get install --yes \
        ca-certificates libexpat1 \
    && rm -rf /var/lib/apt/lists/*

# initially copy only the requirements files
COPY requirements.txt ./
COPY csw ./
COPY esdac ./
COPY inspire ./
COPY mcf-triplify ./
COPY utils ./

RUN pip install -U pip && \
    python3 -m pip install \
    --requirement requirements.txt \
    psycopg2-binary  


