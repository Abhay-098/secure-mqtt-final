#!/usr/bin/env bash
set -e
OUTDIR=certs
mkdir -p ${OUTDIR}/ca ${OUTDIR}/broker ${OUTDIR}/clients

echo "Generating CA (ca/ca.key, ca/ca.crt)..."
openssl genrsa -out ${OUTDIR}/ca/ca.key 4096
openssl req -x509 -new -nodes -key ${OUTDIR}/ca/ca.key -sha256 -days 3650 \
  -subj "/C=IN/ST=SomeState/L=SomeCity/O=MyOrg/CN=MyTestCA" \
  -out ${OUTDIR}/ca/ca.crt

echo "Generating broker key and CSR..."
openssl genrsa -out ${OUTDIR}/broker/broker.key 2048
openssl req -new -key ${OUTDIR}/broker/broker.key \
  -subj "/C=IN/ST=SomeState/L=SomeCity/O=MyOrg/CN=mosquitto.local" \
  -out ${OUTDIR}/broker/broker.csr

echo "Signing broker cert with CA..."
openssl x509 -req -in ${OUTDIR}/broker/broker.csr -CA ${OUTDIR}/ca/ca.crt -CAkey ${OUTDIR}/ca/ca.key -CAcreateserial -out ${OUTDIR}/broker/broker.crt -days 365 -sha256

echo "Generating client certificates (client1 & client2)..."
for client in client1 client2; do
  openssl genrsa -out ${OUTDIR}/clients/${client}.key 2048
  openssl req -new -key ${OUTDIR}/clients/${client}.key -subj "/C=IN/ST=SomeState/L=SomeCity/O=MyOrg/CN=${client}" -out ${OUTDIR}/clients/${client}.csr
  openssl x509 -req -in ${OUTDIR}/clients/${client}.csr -CA ${OUTDIR}/ca/ca.crt -CAkey ${OUTDIR}/ca/ca.key -CAcreateserial -out ${OUTDIR}/clients/${client}.crt -days 365 -sha256
done

echo "Adjusting permissions..."
chmod -R 644 ${OUTDIR}/ca/*.crt ${OUTDIR}/broker/*.crt ${OUTDIR}/clients/*.crt || true
chmod -R 600 ${OUTDIR}/broker/*.key ${OUTDIR}/clients/*.key || true

echo "All certificates created in the 'certs' directory."
