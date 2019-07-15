FROM ubuntu:18.04

# To stop tzdata from pausing the install.
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update
RUN apt-get -y update
RUN apt-get -y upgrade

WORKDIR /home/downloads

# Miniconda
ADD miniconda_install.sh /home/downloads
RUN sh -e miniconda_install.sh
ENV PATH="/root/miniconda3/bin:${PATH}"

# conda installs...
RUN conda install -c anaconda tornado
RUN  conda install -c conda-forge overrides
RUN conda install -c anaconda terminado

# Nodejs
ADD npm_install.sh /home/downloads
RUN sh -e npm_install.sh

# Yarn....
ADD yarn_install.sh /home/downloads
RUN sh -e yarn_install.sh

# App
WORKDIR /home/app
ADD http_server.py /home/app
ADD routes.py /home/app
ADD term_manager.py /home/app
ADD term_rest_handler.py /home/app
ADD term_web_handler.py /home/app
ADD term_websocket_handler.py /home/app
ADD .yarnrc /home/app
ADD yarn.lock /home/app
ADD package.json /home/app
COPY static /home/app/static
COPY templates /home/app/templates
RUN yarn install

CMD python http_server.py
EXPOSE 8888