#!/usr/bin/env bash
set -e

echo "[MikroTik Manager] Starting Home Assistant Ingress Add-on..."

CONFIG_PATH=/data/options.json

if [ -f "$CONFIG_PATH" ]; then
    echo "[MikroTik Manager] Reading options from $CONFIG_PATH..."
    export ROUTER_HOST=$(jq --raw-output '.router_host // "192.168.99.1"' "$CONFIG_PATH")
    export ROUTER_PORT=$(jq --raw-output '.router_port // 8443' "$CONFIG_PATH")
    export ROUTER_USER=$(jq --raw-output '.router_user // "admin"' "$CONFIG_PATH")
    export ROUTER_PASSWORD=$(jq --raw-output '.router_password // ""' "$CONFIG_PATH")
    export USE_SSL=$(jq --raw-output '.use_ssl // true' "$CONFIG_PATH")
    export ALLOW_INSECURE_CERT=$(jq --raw-output '.allow_insecure_cert // true' "$CONFIG_PATH")
    export DEMO_MODE=$(jq --raw-output '.demo_mode // false' "$CONFIG_PATH")
    echo "[MikroTik Manager] Target router: ${ROUTER_HOST}:${ROUTER_PORT} (User: ${ROUTER_USER}, SSL: ${USE_SSL})"
else
    echo "[MikroTik Manager] No /data/options.json found, using defaults or env variables."
fi

export PORT=3000
export NODE_ENV=production

cd /app
exec npx tsx server.ts
