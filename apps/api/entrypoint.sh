#!/bin/sh
# AfriGround API entrypoint — launches uvicorn, optionally with mutual TLS for
# the edge agent bridge (Phase 4.0). Set AGENT_MTLS_ENABLED=1 and point
# AGENT_MTLS_CERT / AGENT_MTLS_KEY / AGENT_MTLS_CA at PEM files to require
# client certificates signed by the AfriGround CA.
set -e

CMD="uvicorn main:app --host 0.0.0.0 --port 8000"

if [ "$AGENT_MTLS_ENABLED" = "1" ]; then
  CMD="$CMD --ssl-certfile ${AGENT_MTLS_CERT:?AGENT_MTLS_CERT required} \
       --ssl-keyfile ${AGENT_MTLS_KEY:?AGENT_MTLS_KEY required} \
       --ssl-ca-certs ${AGENT_MTLS_CA:?AGENT_MTLS_CA required} \
       --ssl-cert-reqs 2"
fi

exec sh -c "$CMD"