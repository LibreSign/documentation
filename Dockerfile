# Etapa 1: Builder da documentação
FROM python:3.11-slim AS builder

WORKDIR /app

# Copia o conteúdo do projeto
COPY . .

# Checagem extra
RUN ls -lah docs && ls -lah docs/conf.py || echo "conf.py não encontrado!"

# Instala dependências do Sphinx (requirements.txt está em /docs)
RUN pip install --upgrade pip \ 
    && pip install -r docs/requirements.txt \
    && pip install --upgrade docutils \
    && pip install sphinx \
    && pip install sphinxcontrib-openapi \
    && pip install sphinxcontrib.redoc

# Faz o build da documentação com tema readthedocs
RUN sphinx-build -b html docs/source docs/_build/html

# Copia a interface do Swagger UI para o builder
# (vai ser repassada depois para a imagem final)
RUN mkdir -p /app/docs/_build/html/swagger
COPY docs/swagger-ui /app/docs/_build/html/swagger

# Nginx para servir os arquivos HTML
FROM nginx:alpine

# Remove o conteúdo padrão do Nginx
RUN rm -rf /usr/share/nginx/html/*

# Copia os arquivos HTML gerados na etapa anterior
COPY --from=builder /app/docs/_build/html /usr/share/nginx/html

# Expõe a porta padrão do Nginx
EXPOSE 80

# CMD ["sphinx-build", "-b", "html", "docs/source", "docs/_build/html"]