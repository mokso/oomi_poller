FROM python:3.13.0-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./*.py ./

CMD [ "python", "./app.py" ]
