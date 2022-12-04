# rmen-app
Russian Macroeconomic Nowcasting App

Пайплайн:

1. Обновление базы данных (пересборка образа и запуск контейнера еженедельно, время парсинга 1-2 минуты). 
```bash
docker build . -f deploy/Dockerfile-parsing -t rmen-parsing
sudo docker run -v [~/science/rmen-app/assets/raw]:/var/rmedb_storage/data rmen-parsing
```
*(заменить ~/science/rmen-app на абсолютный путь до репозитория)*

2. Обновление базы данных (пересборка и запуск еженедельно, после завершения шага 1, время обучения моделей 1-2 минуты).
```bash
docker build . -f deploy/Dockerfile-predict -t rmen-predict
sudo docker run -v [~/science/rmen-app/assets/model]:/var/lib/model rmen-predict
```
*(заменить ~/science/rmen-app на абсолютный путь до репозитория)*

3. Приложение (перезапуск после завершения шага 2, постоянная работа в течение недели до следующего перезапуска).
```bash
docker build . -f deploy/Dockerfile-app -t rmen-app
sudo docker run -p 8050:8050 rmen-app
```
