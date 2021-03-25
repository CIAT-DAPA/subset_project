### STAGE 1: Build ###
FROM node:12.7-alpine AS build
WORKDIR /usr/src/app
COPY ./src/subsets-web/package.json ./
RUN npm install
COPY ./src/subsets-web/ ./
RUN npm run build

### STAGE 2: Run ###
FROM nginx:1.17.1-alpine
COPY ./docker/subsets_web_application/src/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /usr/src/app/dist/subsets-app /usr/share/nginx/html

# cd ..\..\
# docker build -t juancode528/subsets_web_angular .
# or
# docker pull juancode528/subsets_web_angular
# docker run --name subsets_web_app -d -p 8080:80 --link subsets_api:api juancode528/subsets_web_angular:latest