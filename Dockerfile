FROM python:3.10-slim-buster

COPY /mysql/requirements.txt requirements.txt 
# Install required library libmysqlclient (and build-essential for building mysqlclient python extension)
WORKDIR /
RUN set -eux && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential && \
    apt-get install -y default-mysql-client

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN rm -rf /var/lib/apt/lists/*
# if you wish to install mysql client only 
# like in this project to connect external RDS for mysql
# and if you use python as base image
# libmysqlclient and mysqlclient need to be installed together 
# with apt-get. you can't apt-get libmysqlclient
# and then pip install mysqlclient
#RUN useradd -ms /bin/bash apprunner
#USER apprunner
#COPY rds.py /
COPY . .
#CMD [ "python", "/rds_init.py" ]