FROM python:3.11.3-bullseye

COPY common /app/common
ENV PYTHONPATH=/app

ENV STATUS_FILE=/status.txt
HEALTHCHECK --interval=1s --timeout=3s --retries=30 CMD cat ${STATUS_FILE} | grep -q "OK" || exit 1

ARG WORKDIR
COPY ${WORKDIR} /app/${WORKDIR}

WORKDIR /app/${WORKDIR}
RUN pip install -r requirements.txt
ENTRYPOINT python3 app.py