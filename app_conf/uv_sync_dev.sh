#!/bin/sh
if [ -n "$1" ]
then
uv sync --frozen $1
else
uv sync --frozen
fi
