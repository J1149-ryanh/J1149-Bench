FROM ubuntu:18.04

# To stop tzdata from pausing the install.
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update
RUN apt-get -y update
RUN apt-get -y upgrade

RUN mkdir /home/scripts
WORKDIR /home/scripts

# install paicoin
ADD paicoin_install.sh /home/scripts
RUN sh -e paicoin_install.sh

# debugging tools install
ADD debugging_tools_install.sh /home/scripts
RUN sh -e debugging_tools_install.sh

# Miniconda
ADD miniconda_install.sh /home/scripts
RUN sh -e miniconda_install.sh
ENV PATH="/root/miniconda3/bin:${PATH}"

# Add file needed to create username/password for paicoin RPC
RUN ["/bin/bash", "-c", " mkdir -p /root/.paicoin/{testnet,regtest,testnet3}"]
ADD paicoin.conf /root/.paicoin/paicoin.conf
ADD paicoin-testnet.conf /root/.paicoin/testnet/paicoin.conf
ADD paicoin-regtest.conf /root/.paicoin/regtest/paicoin.conf

RUN pwd
ADD paicoin_server.py /home/scripts
ADD rpcauth.py /home/scripts
ADD paicoin_sync.py /home/scripts
WORKDIR /home/scripts
# Make sure both the mainnet and testnet are synced up before we hand it off.
RUN python paicoin_server.py
# Test framework from bitcoin; the paicoin test framework seemed to be too far
# behind to take the risk
RUN pwd
RUN ls
COPY test_framework /home/scripts/test_framework
RUN  conda install -c conda-forge overrides
ADD __init__.py /home/scripts

WORKDIR /home/downloads

# Nodejs
ADD npm_install.sh /home/downloads
RUN sh -e npm_install.sh

# Yarn....
ADD yarn_install.sh /home/downloads
RUN sh -e yarn_install.sh

# App
WORKDIR /home/app
ADD .yarnrc /home/app
ADD yarn.lock /home/app
ADD package.json /home/app
COPY static /home/app/static
COPY templates /home/app/templates
RUN yarn install

RUN  conda install -c anaconda psutil
RUN conda install -c anaconda tornado
RUN conda install -c anaconda terminado

ADD http_server.py /home/app
ADD routes.py /home/app
ADD term_manager.py /home/app
ADD term_rest_handler.py /home/app
ADD term_web_handler.py /home/app
ADD term_websocket_handler.py /home/app

ADD paicoin_repl.py /home/scripts
RUN chmod +x /home/scripts/paicoin_repl.py
ENV PATH="/home/scripts:${PATH}"

CMD python http_server.py

EXPOSE 8888
