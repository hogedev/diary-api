#!/bin/bash
set -e

REPO_URL="https://gitea.honya.dev/honya-dev/diary-api.git"

sudo mkdir -p /opt/diary-api
cd /opt/diary-api

if [ ! -d .git ]; then
  sudo git clone "$REPO_URL" .
else
  sudo git pull
fi

sudo cp -n .env.example .env
JWT=$(openssl rand -hex 32)
sudo sed -i "s/change-me-in-production/$JWT/" .env

echo "=== .env ==="
cat .env

echo "=== docker compose up ==="
sudo docker compose up -d --build

echo "=== waiting ==="
sleep 10

echo "=== containers ==="
sudo docker ps

echo "=== health ==="
curl -s http://localhost:8000/health
