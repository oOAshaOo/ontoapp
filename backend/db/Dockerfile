# pull official base image in 11.4.2
FROM mariadb:11.4.2

# run init-db.sql on init
COPY init_db.sql /docker-entrypoint-initdb.d/
