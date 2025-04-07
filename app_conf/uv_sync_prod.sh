#!/bin/sh
if [ -n "$1" ]
then
uv sync --frozen --no-dev $1
else
uv sync --frozen --no-dev
fi
