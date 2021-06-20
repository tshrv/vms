# syntax=docker/dockerfile:1
FROM python:rc-alpine3.13

WORKDIR /usr/src/vms
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .