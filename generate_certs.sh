#!/usr/bin/env bash
set -euo pipefail
CERT_DIR=${1:-./certs}
mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

echo ">>> Generating CA..."
openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
            -subj "/CN=AtlasPatch CA" -out ca.crt

echo ">>> Generating server certificate..."
openssl genrsa -out server.key 4096
openssl req -new -key server.key -subj "/CN=atlaspatch.local" -out server.csr
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
             -out server.crt -days 825 -sha256

echo ">>> Generating first client certificate..."
openssl genrsa -out client.key 4096
openssl req -new -key client.key -subj "/CN=atlaspatch-agent-1" -out client.csr
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
             -out client.crt -days 825 -sha256

echo "Certificates written to $CERT_DIR"