#!/usr/bin/env bash
set -euo pipefail
CERT_DIR=certs              # dossier où l’on stocke tout
ATLAS_HOST=atlaspatch.local # FQDN ou IP publique de ton serveur
CLIENT_NAME=agent1          # nom CN du 1er agent
SERVER_IP=127.0.0.1

rm -rf "$CERT_DIR" && mkdir "$CERT_DIR"
cd "$CERT_DIR"

############################################
# 1) CA auto-signée
############################################
cat > openssl_ca.cnf <<'EOF'
[req]
distinguished_name = dn
x509_extensions    = v3_ca
prompt             = no

[dn]
CN = AtlasPatch CA

[v3_ca]
basicConstraints   = critical, CA:TRUE
keyUsage           = critical, keyCertSign, cRLSign
subjectKeyIdentifier = hash
EOF

openssl genrsa -out ca.key 4096
openssl req -new -key ca.key -out ca.csr -config openssl_ca.cnf
openssl x509 -req -days 3650 -sha256 \
        -in ca.csr -signkey ca.key -out ca.crt \
        -extfile openssl_ca.cnf -extensions v3_ca
rm openssl_ca.cnf ca.csr

############################################
# 2) CERTIFICAT SERVEUR
############################################
cat > v3_server.ext <<EOF
authorityKeyIdentifier = keyid,issuer
basicConstraints       = CA:FALSE
keyUsage               = critical, digitalSignature, keyEncipherment
extendedKeyUsage       = serverAuth
subjectAltName         = @alt_names

[alt_names]
DNS.1 = ${ATLAS_HOST}
DNS.2 = localhost
IP.1  = ${SERVER_IP}
EOF

openssl genrsa -out server.key 4096
openssl req -new -key server.key -out server.csr -subj "/CN=${ATLAS_HOST}"
openssl x509 -req -days 825 -sha256 \
        -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
        -out server.crt -extfile v3_server.ext
rm server.csr v3_server.ext

############################################
# 3) CERTIFICAT CLIENT (agent1)
############################################
cat > v3_client.ext <<EOF
authorityKeyIdentifier = keyid,issuer
basicConstraints       = CA:FALSE
keyUsage               = critical, digitalSignature, keyEncipherment
extendedKeyUsage       = clientAuth
EOF

openssl genrsa -out "${CLIENT_NAME}.key" 4096
openssl req -new -key "${CLIENT_NAME}.key" -out "${CLIENT_NAME}.csr" -subj "/CN=${CLIENT_NAME}"
openssl x509 -req -days 825 -sha256 \
        -in "${CLIENT_NAME}.csr" -CA ca.crt -CAkey ca.key -CAcreateserial \
        -out "${CLIENT_NAME}.crt" -extfile v3_client.ext
rm "${CLIENT_NAME}.csr" v3_client.ext

echo ">>> Certificats prêts dans: $(pwd)"
