FROM postgres:12

# add backup scripts
COPY containers/postgres/backup.sh /usr/local/bin/backup
COPY containers/postgres/restore.sh /usr/local/bin/restore
COPY containers/postgres/list-backups.sh /usr/local/bin/list-backups

RUN apt-get update &&\
    apt-get install -y postgresql-12-postgis-3-scripts
# make them executable
RUN chmod +x /usr/local/bin/restore
RUN chmod +x /usr/local/bin/list-backups
RUN chmod +x /usr/local/bin/backup
