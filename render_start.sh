#!/usr/bin/env bash
# Used by Render startCommand. Do not use `python` — it is not on PATH at runtime.
set -euo pipefail
exec python3 -m gunicorn core.wsgi:application --bind "0.0.0.0:${PORT}"
