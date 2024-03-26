FROM aapanel/aapanel:lib
USER root
RUN su
#RUN yum -y 1_update.sh && yum upgrade -y

RUN bt 16
RUN touch /www/server/panel/data/ipv6.pl \
&& echo "True" > /www/server/panel/data/ipv6.pl

#Install nginx Tengine2.2
RUN /www/server/panel/install/install_soft.sh 1 install nginx 1.22
#Install mariadb 10.2 (or 10.4)
RUN xxxx/www/server/panel/install/install_soft.sh 1 install php 8.1
#Install PHP 7.4
#RUN xxxx
#Install phpmyadmin 5.0
#RUN xxxx

#Reload AAPanel
RUN bt 1
RUN bt 9

WORKDIR /www/