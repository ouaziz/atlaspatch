#!/usr/bin/env bash
set -euo pipefail
CERT_DIR=${1:-./certs}
mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

echo ">>> Generating CA..."
# Self‑signed CA with proper v3_ca extensions
openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
        -subj "/CN=AtlasPatch CA" \
        -addext "basicConstraints = critical,CA:TRUE" \
        -addext "keyUsage = critical, keyCertSign, cRLSign" \
        -addext "subjectKeyIdentifier = hash" \
        -out ca.crt

echo ">>> Generating server certificate..."
openssl genrsa -out server.key 4096
# CSR with SAN DNS + IP so the cert est reconnu par requests/urllib3
openssl req -new -key server.key \
        -subj "/CN=atlaspatch.local" \
        -addext "subjectAltName = DNS:atlaspatch.local,IP:127.0.0.1" \
        -out server.csr
# Sign with CA + v3 extensions
cat > v3_server.ext <<EOF
basicConstraints=CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:atlaspatch.local,IP:127.0.0.1
EOF

openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
        -days 825 -sha256 -extfile v3_server.ext -out server.crt
rm v3_server.ext

echo ">>> Generating first client certificate..."
openssl genrsa -out client.key 4096
openssl req -new -key client.key -subj "/CN=atlaspatch-agent-1" -out client.csr
cat > v3_client.ext <<EOF
basicConstraints=CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=clientAuth
EOF

openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
        -days 825 -sha256 -extfile v3_client.ext -out client.crt
rm v3_client.ext

echo "Certificates written to $CERT_DIR"
