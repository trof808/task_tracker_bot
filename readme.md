Добавить файл .env с параметрами
```
DATABASE_URL=
TELEGRAM_TOKEN=
```

Добавить файл .env.db с параметрами

```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```

Запустить
```
docker-compose -f docker-compose.dev.yml up --build
```