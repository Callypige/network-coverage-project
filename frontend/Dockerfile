FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine

# Pour Angular v17+ sans outputPath explicite
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

EXPOSE 80
