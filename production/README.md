## Как запустить прод версию.

Установите [докер](https://www.docker.com/)

Создайте в этом каталоге .env файл, как при обычном запуске dev версии сайта, также добавьте туда перменные:

- DB_URL
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB

[Для создания постгрес базы данных](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-20-04)

[Как сделать ссылку на базу данных](https://github.com/jazzband/dj-database-url/)

Добавьте айпи вашего сервера в переменную окружения ALLOWED_HOSTS.

Соберите сайт командой:
```
docker-compose -f docker-compose.prod.yaml build
```

После сборки, поднимите сайт:
```
docker-compose -f docker-compose.prod.yaml up
```
