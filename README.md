# Pour un nouvel agent
openssl genrsa -out client2.key 4096
openssl req -new -key client2.key -subj "/CN=atlaspatch-agent-2" -out client2.csr
openssl x509 -req -in client2.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial \
             -out client2.crt -days 825 -sha256

Fournissez au Laptop : client*.crt, client*.key, et la CA ca.crt.