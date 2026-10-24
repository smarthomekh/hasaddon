ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-nodejs:20
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

WORKDIR /app

# Copy dependency manifests and install production dependencies
COPY package*.json ./
RUN npm install --omit=dev

# Copy compiled production bundle and server code
COPY dist ./dist
COPY server.ts ./
COPY server ./server
COPY src/types ./src/types
COPY src/data ./src/data

# Copy startup script
COPY rootfs /
RUN chmod a+x /etc/services.d/mikrotik/run

EXPOSE 3000
