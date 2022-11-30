FROM python:3.8

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY rmen ./rmen
COPY setup.py ./setup.py
COPY README.md ./README.md
RUN pip install -e .
COPY assets ./assets
COPY app.py ./app.py
# хранилище результатов парсинга
# VOLUME ~/science/rmedb_data/data:assets/data

ENV project_dir .

EXPOSE 8050

CMD [ "gunicorn", "--workers=1", "--threads=1", "-b 0.0.0.0:8050", "app:server"]
