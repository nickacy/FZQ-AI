# FZQ-AI · V24 Frontend Dockerfile
FROM node:20

WORKDIR /app

COPY package.json package-lock.json /app/
RUN npm install

COPY . /app

EXPOSE 3000

CMD ["npm", "start"]
