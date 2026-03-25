# CTFd Docker Plugin Setup Guide

This guide walks through setting up CTFd with remote Docker daemon access via TLS-secured connection. Follow the steps below to configure your Docker server for secure remote access.

## Prerequisites

- A VPS or remote server with Ubuntu/Linux installed
- SSH access to the remote server
- Administrator/root privileges on the remote server

## Setup Steps

### Step 1: Configure Inbound Firewall Rules

First, set up inbound rules on your VPS to allow Docker daemon traffic:

- **Port 2376**: For secure Docker daemon (TLS)
- **Port 2375**: Alternative (not recommended - unencrypted)
- **Port 32768 – 60999**: For Docker container port mappings (or better keep all open)

### Step 2: Install Docker Daemon

Install Docker Engine on your remote server:

For detailed instructions, refer to the [official Docker installation guide](https://docs.docker.com/engine/install/ubuntu/).

### Step 3: Generate TLS Certificates

Run the included `generate-docker-tls.sh` script to generate TLS certificates:

```bash
./generate-docker-tls.sh <your-public-ip>
```

**Example:**
```bash
./generate-docker-tls.sh 203.0.113.45
```

This script generates the following certificates in the `~/docker-tls` directory:
- `ca.pem` - Certificate Authority
- `server-cert.pem` - Server certificate
- `server-key.pem` - Server key
- `cert.pem` - Client certificate
- `key.pem` - Client key

Save these files securely. You'll use them in the next steps.

### Step 4: Configure Docker Daemon for Remote Access

Edit `/etc/docker/daemon.json` on your remote server. If the file doesn't exist, create it:

```json
{
  "hosts": [
    "tcp://0.0.0.0:2376",
    "unix:///var/run/docker.sock"
  ],
  "tls": true,
  "tlsverify": true,
  "tlscacert": "/home/youruser/docker-tls/ca.pem",
  "tlscert": "/home/youruser/docker-tls/server-cert.pem",
  "tlskey": "/home/youruser/docker-tls/server-key.pem"
}
```

**Configuration explanation:**
- `hosts`: Allows connections on both TCP (for remote) and Unix socket (for local)
- `tls`: Enables TLS encryption for secure communication
- `tlsverify`: Requires client certificate verification
- `tlscacert/tlscert/tlskey`: Paths to your generated certificates

Replace `/home/youruser/docker-tls/` with your actual certificate directory.

**Restart Docker to apply changes:**
```bash
sudo systemctl restart docker
```

For more details, see the [Docker remote access documentation](https://docs.docker.com/engine/daemon/remote-access/).

### Step 5: Configure CTFd Docker Plugin

In your CTFd admin panel, navigate to the Docker Plugin settings:

1. **Host**: Enter your remote server's IP address or hostname
2. **Port**: `2376` (default TLS port)
3. **TLS Enabled**: Toggle ON
4. **CA Certificate**: Upload `ca.pem`
5. **Client Certificate**: Upload `cert.pem`
6. **Client Key**: Upload `key.pem`

## Verification

Test the connection from your CTFd instance:

```bash
docker -H tcp://<remote-ip>:2376 \
  --tlsverify \
  --tlscacert=ca.pem \
  --tlscert=cert.pem \
  --tlskey=key.pem \
  info
```

You should see Docker system information if the connection is successful.