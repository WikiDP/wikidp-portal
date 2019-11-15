FROM python:3.6-alpine as builder

LABEL maintainer="carl.wilson@openpreservation.org" \
      org.openpreservation.vendor="Open Preservation Foundation" \
      version="0.1"

RUN  apk update && apk --no-cache --update-cache add gcc build-base libxml2-dev  libxslt-dev

WORKDIR /src

COPY setup.py setup.py
COPY README.md README.md
COPY wikidp/* wikidp/

RUN mkdir /install && pip install -U pip && pip install --install-option="--prefix=/install" .

FROM python:3.6-alpine

RUN apk update && apk add --no-cache --update-cache libc6-compat libstdc++ bash
RUN install -d -o root -g root -m 755 /opt && adduser -h /opt/wikidp -S wikidp && pip install -U pip python-dateutil

USER wikidp

WORKDIR /opt/wikidp

COPY --from=builder /install /usr/local
COPY . /opt/wikidp/

EXPOSE 5000
ENTRYPOINT /opt/wikidp/run.sh
