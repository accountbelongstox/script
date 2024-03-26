FROM debian:latest

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get update \
    && apt-get install -y curl \
    && apt-get -y autoclean

ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION 18.16.0
ENV NPM_REGISTRY=https://registry.npmmirror.com

ENV NVM_NODEJS_ORG_MIRROR https://npm.taobao.org/mirrors/node/

COPY nvm-0.39.7.tar.gz /tmp/nvm.tar.gz
COPY run_script.sh /usr/local/run_script.sh

RUN mkdir -p $NVM_DIR \
    && tar xzf /tmp/nvm.tar.gz --strip-components=1 -C $NVM_DIR \
    && echo 'export NVM_DIR="$NVM_DIR"' >> /etc/profile \
    && echo '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"  # This loads nvm' >> /etc/profile \
    && chmod +x /usr/local/run_script.sh \
    && source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && npm config set registry $NPM_REGISTRY \
    && npm install yarn -g \
    && nvm alias default $NODE_VERSION \
    && nvm use default \
    && chmod +x /usr/local/run_script.sh \
    && echo 'export NVM_DIR="$HOME/.nvm"' >> "$HOME/.bashrc" \
    && echo '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"  # This loads nvm' >> "$HOME/.bashrc" \
    && echo '[ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion" # This loads nvm bash_completion' >> "$HOME/.bashrc"

ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

CMD ["bash", "/usr/local/run_script.sh"]
