ARG BUILD_FROM=ghcr.io/home-assistant/base:latest
FROM ${BUILD_FROM}

# Set environment
ENV LANG=C.UTF-8 \
    PORT=3000 \
    NODE_ENV=production

# Install Node.js, npm, bash, curl, and jq
RUN apk add --no-cache \
    nodejs \
    npm \
    bash \
    curl \
    jq

WORKDIR /app

# Copy dependency manifests and install dependencies
COPY package*.json ./
RUN npm install

# Copy application source code
COPY . .

# Build client production Vite bundle
RUN npm run build

# Make startup script executable
COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 3000

CMD [ "/run.sh" ]
