ARG BUILD_FROM=node:20-alpine
FROM ${BUILD_FROM}

ENV LANG C.UTF-8
ENV PORT 3000
ENV NODE_ENV production

# Install essential runtime tools
RUN apk add --no-cache bash curl jq

WORKDIR /app

# Copy dependency manifests and install dependencies
COPY package*.json ./
RUN npm install

# Copy application source code
COPY . .

# Build client production Vite bundle
RUN npm run build

# Copy and setup startup script
COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 3000

CMD [ "/run.sh" ]
