# Dockerfile
FROM ghcr.io/home-assistant/amd64-base-python:3.9-alpine3.16
WORKDIR /usr/src
ENV LANG C.UTF-8
COPY run.sh /
COPY main.py /usr/src/
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]
