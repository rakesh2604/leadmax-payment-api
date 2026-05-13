#!/usr/bin/env bash
set -o errexit

WORKERS="${WEB_CONCURRENCY:-1}"

exec python3 -m gunicorn core.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --access-logfile - \
  --error-logfile - \
  --workers "${WORKERS}"