FROM alpine:3.9

FROM alpine:3.9 AS build_stage

LABEL maintainer "robert@aztek.io"

# hadolint ignore=DL3018
RUN apk --update --no-cache add \
        autoconf \
        autoconf-doc \
        automake \
        c-ares \
        c-ares-dev \
        curl \
        gcc \
        libc-dev \
        libevent \
        libevent-dev \
        libtool \
        make \
        libressl-dev \
        file \
        pkgconf \
        tar \
        gzip

ARG PGBOUNCER_VERSION

RUN curl -Lso  "/tmp/pgbouncer.tar.gz" "https://pgbouncer.github.io/downloads/files/${PGBOUNCER_VERSION}/pgbouncer-${PGBOUNCER_VERSION}.tar.gz" && \
        file "/tmp/pgbouncer.tar.gz"

WORKDIR /tmp

RUN mkdir /tmp/pgbouncer && \
        tar -zxvf pgbouncer.tar.gz -C /tmp/pgbouncer --strip-components 1

WORKDIR /tmp/pgbouncer

RUN ./configure --prefix=/usr && \
        make

FROM alpine:3.9

# hadolint ignore=DL3018
RUN apk --update --no-cache add \
        libevent \
        libressl \
        ca-certificates \
        c-ares

WORKDIR /etc/pgbouncer
#COPY containers/pgbouncer/pgbouncer.ini /etc/pgbouncer/pgbouncer.ini
#COPY containers/pgbouncer/databases /etc/pgbouncer/databases
#RUN echo "[databases]" >> /etc/pgbouncer/databases
#RUN echo ""${POSTGRES_DB}" = host="${POSTGRES_HOST}" dbname="${POSTGRES_DB}" port="$POSTGRES_PORT}""  >> /etc/pgbouncer/databases
#RUN cat /etc/pgbouncer/databases

#COPY containers/pgbouncer/userlist.txt /etc/pgbouncer/userlist.txt
#RUN echo "\""${POSTGRES_USER}"\" \""${POSTGRES_PASSWORD}"\"" >> /etc/pgbouncer/userlist.txt
#RUN cat /etc/pgbouncer/userlist.txt

WORKDIR /var/log/pgbouncer

RUN chown -R postgres:root \
        /etc/pgbouncer \
        /var/log/pgbouncer

USER postgres

COPY --from=build_stage --chown=postgres ["/tmp/pgbouncer", "/opt/pgbouncer"]
COPY --chown=postgres ["containers/pgbouncer/entrypoint.sh", "/opt/pgbouncer"]
RUN chmod +x /opt/pgbouncer/entrypoint.sh

WORKDIR /opt/pgbouncer
ENTRYPOINT ["/opt/pgbouncer/entrypoint.sh"]
