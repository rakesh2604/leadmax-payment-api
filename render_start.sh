#!/usr/bin/env bash
set -o errexit
python3 manage.py migrate --noinput
WORKERS="${WEB_CONCURRENCY:-1}"
if [ -z "$WORKERS" ]; then
  WORKERS=1
fi
exec python3 -m gunicorn core.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --access-logfile - \
  --error-logfile - \
  --timeout 120 \
  --workers "${WORKERS}"
