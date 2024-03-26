FROM debian:latest

LABEL maintainer="Peter Dave Hello <hsu@peterdavehello.org>"
LABEL name="nvm-dev-env"
LABEL version="latest"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV DEBIAN_FRONTEND noninteractive
ENV DEBIAN_APT_SITE mirrors.tuna.tsinghua.edu.cn
ENV NPM_REGISTRY https://registry.npm.taobao.org

RUN sed -E -i "s/([a-z]+.)?deb.debian.org/$DEBIAN_APT_SITE/g" /etc/apt/sources.list
RUN sed -i "s/security.debian.org/$DEBIAN_APT_SITE/g" /etc/apt/sources.list

RUN apt update         && \
    apt upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"  && \
    apt install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"     \
        coreutils             \
        util-linux            \
        bsdutils              \
        file                  \
        openssl               \
        libssl-dev            \
        locales               \
        ca-certificates       \
        ssh                   \
        wget                  \
        patch                 \
        sudo                  \
        htop                  \
        dstat                 \
        vim                   \
        tmux                  \
        curl                  \
        git                   \
        jq                    \
        zsh                   \
        ksh                   \
        gcc                   \
        g++                   \
        xz-utils              \
        build-essential       \
        bash-completion       && \
    apt-get clean

COPY shellcheck-v0.7.0.linux.x86_64.tar.xz /tmp/
RUN tar xJvf /tmp/shellcheck-v0.7.0.linux.x86_64.tar.xz -C /tmp/ && \
    mv /tmp/shellcheck-v0.7.0/shellcheck /bin && \
    rm -rf /tmp/shellcheck-v0.7.0
RUN shellcheck -V

RUN locale-gen en_US.UTF-8

RUN bash --version | head -n 1
RUN zsh --version
RUN ksh --version || true
RUN dpkg -s dash | grep ^Version | awk '{print $2}'
RUN git --version
RUN curl --version
RUN wget --version

RUN useradd -ms /bin/bash nvm

COPY run_script.sh /usr/local/run_script.sh
COPY . /home/nvm/.nvm/
RUN chown nvm:nvm -R "/home/nvm/.nvm"

# Create a separate sudoers file for nvm
RUN echo 'nvm ALL=(ALL:ALL) NOPASSWD: ALL' > /etc/sudoers.d/nvm_sudo

# Set up environment for nvm user
USER nvm

RUN echo 'export NVM_DIR="$HOME/.nvm"'                                       >> "$HOME/.bashrc" && \
    echo '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"  # This loads nvm' >> "$HOME/.bashrc" && \
    echo '[ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion" # This loads nvm bash_completion' >> "$HOME/.bashrc" && \
    echo "npm config set registry $NPM_REGISTRY" >> "$HOME/.bashrc"

# Set WORKDIR and CMD for nvm user
USER root
WORKDIR /home/nvm/.nvm

# Set up environment for root user
RUN echo 'export NVM_DIR="/root/.nvm"'                                       >> "/root/.bashrc" && \
    echo '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"  # This loads nvm' >> "/root/.bashrc" && \
    echo '[ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion" # This loads nvm bash_completion' >> "/root/.bashrc" && \
    echo "npm config set registry $NPM_REGISTRY" >> "/root/.bashrc"

CMD ["bash", "/usr/local/run_script.sh"]
