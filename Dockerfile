FROM python:3.11.3-bullseye

ARG WORKDIR
COPY ${WORKDIR} /app/${WORKDIR}
COPY common /app/common
ENV PYTHONPATH=/app

WORKDIR /app/${WORKDIR}
RUN pip install -r requirements.txt
ENTRYPOINT python3 app.py