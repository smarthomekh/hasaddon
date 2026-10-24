#!/usr/bin/with-contenv bashio
# Home Assistant Add-on Run Script for MikroTik Manager

CONFIG_PATH=/data/options.json

export ROUTER_HOST=$(bashio::config 'router_host')
export ROUTER_PORT=$(bashio::config 'router_port')
export ROUTER_USER=$(bashio::config 'router_user')
export ROUTER_PASSWORD=$(bashio::config 'router_password')
export USE_SSL=$(bashio::config 'use_ssl')
export ALLOW_INSECURE_CERT=$(bashio::config 'allow_insecure_cert')
export DEMO_MODE=$(bashio::config 'demo_mode')
export PORT=3000

bashio::log.info "Starting MikroTik Manager for Home Assistant..."
bashio::log.info "Target Router: ${ROUTER_HOST}:${ROUTER_PORT} (User: ${ROUTER_USER})"

cd /app
exec npx tsx server.ts
