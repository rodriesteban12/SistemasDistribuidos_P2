#!/bin/bash
set -e  

export pagina_text=${pagina_text:-"Default Hello World! Env var was not set! :O"}

/usr/local/bin/confd -onetime -backend env

echo "Starting webpage!"
exec python app.py
