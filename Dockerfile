FROM python:3.12.13-bookworm
LABEL maintainer="genuchten@yahoo.com"

ENV VENV=/opt/venv
ENV PATH="$VENV/bin:$PATH"

RUN apt-get update && apt-get install --yes \
        ca-certificates libexpat1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ROOT

# create virtualenv
RUN python3 -m venv $VENV

# initially copy only the requirements files
COPY cordis-projects ./cordis-projects
COPY CSVW ./CSVW
COPY csw ./csw
COPY data.europa.eu ./data.europa.eu
COPY doi-completer ./doi-completer
COPY impact4soil ./impact4soil
COPY newsfeeds ./newsfeeds
COPY prepsoil ./prepsoil
COPY utils ./utils

RUN pip install -U pip && \
    python3 -m pip install -r csw/requirements.txt \
    psycopg2-binary && \
    python3 -m pip install -r data.europa.eu/requirements.txt && \
    python3 -m pip install -r doi-completer/requirements.txt && \
    python3 -m pip install -r newsfeeds/requirements.txt && \
    python3 -m pip install -r prepsoil/requirements.txt && \ 
    python3 -m pip install -r CSVW/requirements.txt 
