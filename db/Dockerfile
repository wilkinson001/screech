FROM mysql:5.6

ARG MYSQL_USER
ARG MYSQL_PASSWORD
ARG MYSQL_DATABASE

COPY db3.sql /docker-entrypoint-initdb.d/db.sql

RUN service mysql start