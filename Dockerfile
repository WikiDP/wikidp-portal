FROM python:3.6-alpine as builder

LABEL maintainer="carl.wilson@openpreservation.org" \
      org.openpreservation.vendor="Open Preservation Foundation" \
      version="0.1"

RUN  apk update && apk --no-cache --update-cache add gcc build-base libxml2-dev git libxslt-dev

WORKDIR /src
RUN git clone https://github.com/WikiDP/wikidp-portal.git
RUN mkdir /install && cd /src/wikidp-portal && pip install -U pip && pip install --install-option="--prefix=/install" .

FROM python:3.6-alpine

RUN apk update && apk add --no-cache --update-cache libc6-compat libstdc++ bash
RUN install -d -o root -g root -m 755 /opt && adduser -h /opt/wikidp -S wikidp && pip install -U pip python-dateutil

WORKDIR /opt/wikidp

COPY --from=builder /install /usr/local
COPY . /opt/wikidp/
RUN chown -R wikidp:users /opt/wikidp

USER wikidp

EXPOSE 5000
ENV FLASK_APP='wikidp'
ENTRYPOINT flask run --host "0.0.0.0" --port "5000"
