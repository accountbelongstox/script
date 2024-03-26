FROM node:18
ENV EXPOSE_PORT 1800-1899
RUN npm config set registry https://registry.npmmirror.com
RUN #npm install -g npm
ENV NPM_CONFIG_LOGLEVEL=warn
ENV NPM_CONFIG_COLOR=false
ENV HOST 0.0.0.0
ENV APP_ROOT /www
ENV SERVER_ROOT /www/pm2_node18
ENV EXPOSE_HTTP 80
ENV EXPOSE_HTTPS 443
#RUN npm install pm2 -g
#RUN npm install yarn -g
EXPOSE $EXPOSE_PORT $EXPOSE_HTTP $EXPOSE_HTTPS
WORKDIR ${SERVER_ROOT}
COPY manager_server .
#RUN npm i
COPY install.sh .
CMD sh -c 'chmod -R 777 /www && chmod -R 777 /www/pm2_node18/install_nodemodules.sh && /www/pm2_node18/install_nodemodules.sh && node /www/pm2_node18/manager_server/server.js'