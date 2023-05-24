FROM node:18
WORKDIR /code/

COPY . /code/

RUN npm ci --dev
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"


FROM python:latest
WORKDIR /code/

EXPOSE 8000

COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

RUN python3 manage.py collectstatic --noinput
VOLUME ["/media", "./db.sqlite3"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
