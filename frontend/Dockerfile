FROM node:16.16.0

COPY package.json package-lock.json /code/
ADD /bundles-src/ /code/bundles-src/
WORKDIR /code/

RUN npm ci
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
