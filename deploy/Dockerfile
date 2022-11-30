FROM python:3.8

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY rmen ./rmen
COPY assets ./assets
COPY app ./app
# хранилище результатов парсинга
RUN -v C:/Users/migareev/Documents/rmedb_data/data:assets/data

EXPOSE 8050

CMD ["python", "./app/app.py"]