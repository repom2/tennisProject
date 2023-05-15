FROM node:16-alpine

RUN npm install -g json-server

WORKDIR /app
COPY docker/json-server/fixtures.json .

ENTRYPOINT ["json-server", "--port", "8001", "--host", "0.0.0.0"]

EXPOSE 8081

CMD ["/app/fixtures.json"]