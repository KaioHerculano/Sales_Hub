FROM python:3.12-slim

WORKDIR /Sales_Hub

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y git

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#RUN python manage.py migrate

EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000
