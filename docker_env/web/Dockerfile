FROM harbor.gtjaqh.io/tradeapi/web-base:latest
WORKDIR /web/
COPY web/. .
RUN yarn install --registry=https://mirrors.gtjaqh.io/repository/npm/
RUN yarn build

FROM docker.gtjaqh.io/library/nginx:alpine
COPY ./docker_env/nginx/my.conf /etc/nginx/conf.d/my.conf
COPY --from=0 /web/dist /usr/share/nginx/html
