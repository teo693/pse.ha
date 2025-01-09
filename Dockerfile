# Dockerfile
FROM homeassistant/amd64-base-python:3.11-alpine3.19
WORKDIR /usr/src
ENV LANG C.UTF-8
COPY run.sh /
COPY main.py /usr/src/
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]
