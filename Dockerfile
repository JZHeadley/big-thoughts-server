FROM python:3.7
RUN pip3 install pipenv
WORKDIR /usr/src/app

COPY Pipfile ./
COPY Pipfile.lock ./

# RUN set -ex && pipenv install --deploy --system
RUN pip install flask twilio flask-sockets flask-cors flask-sqlalchemy gunicorn psycopg2

COPY . .

EXPOSE 5000

ENV TWILIO_TOKEN 58779a2c0fb69b8a3fe2b939d0d50275
ENV TWILIO_SID ACa419e2930a99b69f74d68a01ee360617                                                                                     

CMD [ "gunicorn", "-b0.0.0.0:5000", "app:app" ]