#!/bin/bash

set -e

# ===== INPUT =====
if [ -z "$1" ]; then
  echo "Usage: $0 <public-ip> [public-dns]"
  exit 1
fi

PUBLIC_IP=$1
PUBLIC_DNS=$2
CERT_DIR="$HOME/docker-tls"
DAYS=365

mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

echo "[+] PUBLIC_IP=$PUBLIC_IP"
echo "[+] PUBLIC_DNS=$PUBLIC_DNS"
echo "[+] CERT_DIR=$CERT_DIR"

# ===== CA =====
openssl genrsa -out ca-key.pem 4096

openssl req -new -x509 -days $DAYS \
  -key ca-key.pem -sha256 -out ca.pem \
  -subj "/CN=docker-ca"

# ===== SERVER =====
openssl genrsa -out server-key.pem 4096

openssl req -new -key server-key.pem \
  -out server.csr -subj "/CN=$PUBLIC_IP"

PRIVATE_IP=$(hostname -I | awk '{print $1}')

SAN="subjectAltName=IP:$PUBLIC_IP,IP:$PRIVATE_IP,IP:127.0.0.1"
if [ -n "$PUBLIC_DNS" ]; then
  SAN="$SAN,DNS:$PUBLIC_DNS"
fi

echo "$SAN" > extfile.cnf
echo "extendedKeyUsage=serverAuth" >> extfile.cnf

openssl x509 -req -days $DAYS -sha256 \
  -in server.csr -CA ca.pem -CAkey ca-key.pem \
  -CAcreateserial -out server-cert.pem \
  -extfile extfile.cnf

# ===== CLIENT =====
openssl genrsa -out key.pem 4096

openssl req -new -key key.pem \
  -out client.csr -subj "/CN=client"

echo "extendedKeyUsage=clientAuth" > extfile-client.cnf

openssl x509 -req -days $DAYS -sha256 \
  -in client.csr -CA ca.pem -CAkey ca-key.pem \
  -CAcreateserial -out cert.pem \
  -extfile extfile-client.cnf

# ===== PERMS =====
chmod 0400 ca-key.pem server-key.pem key.pem
chmod 0444 ca.pem server-cert.pem cert.pem

echo "[✓] Done → $CERT_DIR"