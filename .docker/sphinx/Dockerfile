FROM python:3.11-slim

WORKDIR /app
VOLUME ["/app"]

COPY scripts /scripts

ENTRYPOINT ["/scripts/entrypoint.sh"]