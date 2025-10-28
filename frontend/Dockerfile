# === ETAPA 1: Construcción (Build) ===
# Usamos una imagen oficial de Node.js v18 sobre Alpine Linux (ligera) como base.
FROM node:18-alpine AS builder

# Establecemos el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copiamos los archivos de definición de dependencias.
# El '*' asegura que copiemos tanto package.json como package-lock.json.
COPY package*.json ./

# Instalamos las dependencias del proyecto.
RUN npm install

# Copiamos el resto del código fuente de la aplicación.
COPY . .

# Ejecutamos el script de build definido en package.json ("vite build").
# Esto generará la carpeta /app/dist con los archivos estáticos.
RUN npm run build

# === ETAPA 2: Servidor (Serve) ===
# Usamos una imagen muy ligera de Nginx para servir los archivos estáticos.
FROM nginx:1.25-alpine

# Copiamos los archivos de producción generados en la etapa anterior
# desde la imagen 'builder' al directorio por defecto de Nginx.
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiamos nuestro archivo de configuración personalizado para Nginx.
# Esto es CRUCIAL para que React Router funcione correctamente.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponemos el puerto 80, que es el puerto por defecto de Nginx.
EXPOSE 80

# El comando que se ejecuta cuando el contenedor se inicia.
CMD ["nginx", "-g", "daemon off;"]