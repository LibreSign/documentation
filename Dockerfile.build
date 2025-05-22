FROM python:3.11-slim

WORKDIR /app
COPY docs /app/docs

RUN pip install --upgrade pip && \
    pip install -r /app/docs/requirements.txt

RUN mkdir -p /app/docs/_build/html/swagger
COPY ./docs/swagger-ui /app/docs/swagger-ui


# Gera os HTMLs das documentações
CMD sphinx-build -b html /app/docs/user /app/docs/_build/user && \
    sphinx-build -b html /app/docs/admin /app/docs/_build/admin && \
    sphinx-build -b html /app/docs/dev /app/docs/_build/dev
