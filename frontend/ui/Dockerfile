# pull official base image in 23.1.0
FROM node:23.1.0-alpine

WORKDIR /app

COPY . .

RUN npm install

RUN npm run build

CMD ["npm", "run", "preview"]
