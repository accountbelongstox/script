# CGO_ENABLED=1 GOOS=linux CC=x86_64-unknown-linux-gnu-gcc CXX=x86_64-unknown-linux-gnu-g++ GOARCH=amd64 go build -ldflags "-X 'github.com/0xJacky/Nginx-UI/server/settings.buildTime=$(date +%s)'" -o nginx_ui -v main.go
FROM --platform=$TARGETPLATFORM uozi/nginx-ui-base:latest
WORKDIR /tmp
COPY nginx-ui-linux-64/nginx-ui.tar.gz .
RUN tar -zxvf nginx-ui.tar.gz

WORKDIR /app
EXPOSE 80 443

#COPY resources/docker/run.sh /app/run.sh
COPY resources/docker/ojbk.me /etc/nginx/sites-available/ojbk.me
COPY resources/docker/app.ini /etc/nginx-ui/app.ini
COPY resources/docker/demo.db /etc/nginx-ui/database.db
COPY resources/docker/nginx.conf /etc/nginx/nginx.conf
COPY resources/docker/nginx-ui.conf /etc/nginx/conf.d/nginx-ui.conf
COPY resources/docker/start.sh /app/start.sh
#COPY nginx-ui-$TARGETOS-$TARGETARCH$TARGETVARIANT/nginx-ui /app/nginx-ui

#RUN cd /app && chmod a+x run.sh && rm -f /etc/nginx/conf.d/default.conf
RUN cp /tmp/nginx-ui /app/nginx-ui && mkdir -p /var/www && chmod a+x /app/run.sh && chmod -R 777 /var/www \
    && rm -f /etc/nginx/conf.d/default.conf  \
    && rm -f /usr/etc/nginx/conf.d/default.conf

ENTRYPOINT ["./start.sh"]
