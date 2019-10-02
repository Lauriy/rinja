FROM python:3.7 AS builder

WORKDIR /home/docker/rinja

COPY requirements.txt ./

RUN apt-get update && apt-get install libfann-dev python3-fann2 swig -y

RUN pip install --upgrade setuptools pip wheel && \
    pip wheel -r requirements.txt --wheel-dir=./wheels/

ENTRYPOINT ["pytest"]

FROM python:3.7-slim AS deployer

LABEL maintainer="Lauri Elias <lauri.elias@indoorsman.ee>"

RUN apt-get update && apt-get install libfann-dev python3-fann2 swig python-opencv -y && apt-get autoremove -y \
    && apt-get autoclean

WORKDIR /home/docker/rinja

COPY --from=builder /home/docker/rinja/wheels ./wheels

COPY requirements.txt manage.py ./

COPY rinja ./rinja

COPY templates ./templates

COPY docker-entrypoint.sh /usr/local/bin/

RUN pip install --no-index --find-links=wheels -r requirements.txt && \
    chmod +x /usr/local/bin/docker-entrypoint.sh && \
    rm -rf requirements.txt wheels

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
