FROM python:3.7
RUN pip3 install pipenv
WORKDIR /usr/src/app

COPY Pipfile ./
COPY Pipfile.lock ./

RUN set -ex && pipenv install --deploy --system

COPY . .

EXPOSE 8000

ENV TWILIO_TOKEN a1157e60d68c0f0bf618c1b8580c1110
ENV TWILIO_SID AC6c5a5b034372ecd01df7096d871dd72f                                                                                     

CMD [ "gunicorn", "-b0.0.0.0:8000", "app:app" ]