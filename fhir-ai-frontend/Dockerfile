# build
FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm i
RUN npm run build

# runtime
FROM nginx:alpine
RUN rm /etc/nginx/conf.d/default.conf

COPY --from=build /app/dist/fhir-ai-frontend/browser/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]