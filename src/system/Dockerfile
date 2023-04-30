FROM python:3.11.3-bullseye AS base

COPY shared /app/shared
COPY system/common /app/system/common
ENV PYTHONPATH=/app:/app/system

ENV STATUS_FILE=/status.txt
HEALTHCHECK --interval=1s --timeout=3s --retries=30 CMD cat ${STATUS_FILE} | grep -q "OK" || exit 1

ARG WORKDIR
ENV WORKDIR=${WORKDIR}
WORKDIR /app/system/${WORKDIR}
COPY system/${WORKDIR} .
RUN pip install -r requirements.txt

WORKDIR /app
SHELL ["/bin/bash", "-c"]
# replace / in WORKDIR with .
ENTRYPOINT python3 -m system.${WORKDIR//\//.}.app

FROM base AS aggregators
COPY system/aggregators/common /app/system/aggregators/common

FROM base AS reducers
COPY system/reducers/common /app/system/reducers/common