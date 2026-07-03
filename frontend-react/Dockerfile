# FZQ-AI · V24 Frontend Dockerfile
FROM node:20 AS builder

WORKDIR /app

COPY package.json package-lock.json /app/
RUN npm ci

COPY . /app
RUN npm run build

# ── Runtime: serve the built bundle via `vite preview` ──
FROM node:20-slim

WORKDIR /app

# Only the built artifacts + manifest are needed at runtime
COPY --from=builder /app/package.json /app/package-lock.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/vite.config.ts ./vite.config.ts
COPY --from=builder /app/index.html ./index.html
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
