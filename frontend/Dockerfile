# === ETAPA 1: Build ===
FROM node:18-alpine AS builder
WORKDIR /app

# Instala deps de forma determinista
COPY package*.json ./
RUN npm ci

# Copia el resto del código y construye
COPY . .
RUN npm run build

# === ETAPA 2: Nginx para servir estáticos ===
FROM nginx:1.25-alpine
# Copia el build
COPY --from=builder /app/dist /usr/share/nginx/html
# Configuración para SPA (React Router)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
