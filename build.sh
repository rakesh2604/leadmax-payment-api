#!/usr/bin/env bash
set -o errexit

export PIP_NO_CACHE_DIR=1

python3 -m pip install --upgrade pip
python3 -m pip install --no-cache-dir -r requirements.txt

python3 manage.py migrate
python3 manage.py collectstatic --noinput