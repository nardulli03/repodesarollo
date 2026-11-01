FROM node:24-bookworm-slim

WORKDIR /app

RUN npm install -g pnpm@11.13.0

COPY package.json pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile

COPY index.html vite.config.js ./
COPY src ./src
COPY public ./public

EXPOSE 5173

CMD ["pnpm", "dev", "--host", "0.0.0.0"]
