#!/bin/sh

docker volume create data
docker run --rm --mount src=data,dst=/data alpine mkdir -p \
  /data/app1 \
  /data/app2

