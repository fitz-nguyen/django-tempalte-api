FROM nginx:1.17.10-alpine

ARG ENVIRONMENT

#COPY containers/nginx/nginx.conf /etc/nginx/nginx.conf
COPY containers/nginx/conf.d/api.conf /etc/nginx/conf.d/api.conf
COPY containers/nginx/sites-enabled/default /etc/nginx/sites-enabled/default

# install filebeats for nginx
#RUN wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.0.1-amd64.deb
#RUN sudo dpkg -i filebeat-7.0.1-amd64.deb
#RUN filebeat modules enable nginx

EXPOSE 80

COPY containers/nginx/start.sh /

RUN mkdir -p /usr/src/api
RUN mkdir -p /usr/src/api_staticfiles
RUN mkdir -p /usr/src/api_media

# 10.Permission 755 allows the execute permission for all users to run the script
RUN chmod 755 /start.sh

# 11.Execute the script
#CMD ["/start.sh"]