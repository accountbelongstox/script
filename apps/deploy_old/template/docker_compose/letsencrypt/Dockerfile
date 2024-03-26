#FROM ubuntu:18.04
#MAINTAINER Eranga Bandara (erangaeb@gmail.com)
#RUN apt-get 1_update.sh -y
#RUN apt-get install -y software-properties-common
#RUN add-apt-repository -y ppa:nginx/stable
#RUN apt-get 1_update.sh -y
#RUN apt-get install -y nginx
#RUN add-apt-repository ppa:certbot/certbot
#RUN apt-get 1_update.sh -y
#RUN apt-get install -y certbot python-certbot-nginx
#RUN echo "\ndaemon off;" >> /etc/nginx/nginx.conf
#RUN chown -R www-data:www-data /var/lib/nginx
#ADD config/climguards-live.com /etc/nginx/sites-available/climguards.com
#RUN ln -s /etc/nginx/sites-available/climguards.com /etc/nginx/sites-enabled/climguards
# add self signed climguards server certs until generating certs via certbot
# otherwise nginx will stop since no certificates found
#ADD certs/server.crt /etc/letsencrypt/live/climguards.com/fullchain.pem
#ADD certs/server.key /etc/letsencrypt/live/climguards.com/privkey.pem