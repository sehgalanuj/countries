FROM python:3.12.4-alpine3.20

COPY app.py .
COPY templates/index.html /templates/index.html
COPY templates/admin.html /templates/admin.html
COPY templates/login.html /templates/login.html
COPY templates/error.html /templates/error.html
COPY static/custom.geo.json /static/custom.geo.json
COPY static/logo.png /static/logo.png
COPY saml/settings.json /saml/settings.json
COPY requirements.txt .

EXPOSE 5002

RUN apk update
RUN apk --no-cache add \
    libxml2-dev \
    xmlsec-dev \
    openssl-dev \
    pkgconfig \
    musl-dev \
    gcc \
    bash \
    emacs

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "app.py"]
