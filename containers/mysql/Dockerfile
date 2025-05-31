FROM mysql:5.7

ENV MYSQL_DATABASE: 'seniorApp'
# So you don't have to use root, but you can if you like
ENV MYSQL_USER 'root'
# You can use whatever password you like
ENV MYSQL_PASSWORD 'root'
# Password for root access
ENV MYSQL_ROOT_PASSWORD 'root'

RUN echo "bind-address = 0.0.0.0" >> /etc/mysql/mysql.conf.d/mysqld.cnf