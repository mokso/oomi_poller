FROM python:3.13.0

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and dependencies
RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils
RUN python -m playwright install --with-deps chromium

COPY ./*.py ./

CMD [ "python", "./app.py" ]
