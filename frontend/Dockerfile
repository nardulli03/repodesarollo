# syntax=docker/dockerfile:1

# Node 24 conserva compatibilidad con las herramientas actuales del proyecto.
FROM node:24-alpine AS builder

WORKDIR /app

RUN npm install --global pnpm@11.13.0

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY index.html vite.config.js ./
COPY src ./src
COPY public ./public

RUN pnpm run build


FROM nginx:1.30.6-alpine-slim AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist/ /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
