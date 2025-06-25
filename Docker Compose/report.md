# Лабораторная работа №2 (*)

## Задания

1. Написать “плохой” Docker compose файл, в котором есть не менее трех “bad practices” по их написанию.
2. Написать “хороший” Docker compose файл, в котором эти плохие практики исправлены.
3. В Readme описать каждую из плохих практик в плохом файле, почему она плохая и как в хорошем она была исправлена, как исправление повлияло на результат.
4. После предыдущих пунктов в хорошем файле настроить сервисы так, чтобы контейнеры в рамках этого compose-проекта так же поднимались вместе, но не "видели" друг друга по сети. В отчете описать, как этого добились и кратко объяснить принцип такой изоляции.

## Что такое Docker Compose

* Перед началом выполнения лабораторной работы вкратце разберем что из себя представляет **Docker Compose** и чем он отличается от **Docker** из прошлой лабораторной работы.
* Docker Compose — это инструментальное средство, входящее в состав Docker. Оно предназначено для решения задач, связанных с развёртыванием проектов.
* Docker применяется для управления отдельными контейнерами (сервисами), из которых состоит приложение.
* Docker Compose используется для одновременного управления несколькими контейнерами, входящими в состав приложения. Этот инструмент предлагает те же возможности, что и Docker, но позволяет работать с более сложными приложениями.

![image](https://github.com/user-attachments/assets/2149951f-2038-4fd2-afd9-44563212a330)

## Создание проекта

* Перед написанием `Docker Compose` - файла создадим небольшой php-проект, который будет выводить в окно нашего браузера приветствующее сообщение.

 ![Снимок экрана от 2024-11-23 08-57-58](https://github.com/user-attachments/assets/dd729744-c113-4f54-b260-e65c72e994af)

* Соберем образ.

![Снимок экрана от 2024-11-23 09-04-40](https://github.com/user-attachments/assets/7683f2b8-7ad0-4555-84e8-e8d03208d037)

* Командой `sudo docker images` - проверяем, что наш образ успешно собрался.

![Снимок экрана от 2024-11-23 09-05-45](https://github.com/user-attachments/assets/8e9554e3-9dcd-4b7b-a2dd-8340153169fc)

* `sudo docker run php-apache-app` - запускаем котнейнер и проверяем его работу.

![Снимок экрана от 2024-11-23 09-57-08](https://github.com/user-attachments/assets/7dc839bd-ee80-475d-93ac-35b0b5d0f4a6)

## Плохой Docker Compose

>  Сначала зайдем на **DockerHub** (https://hub.docker.com/), откуда подтянем несколько готовых образов. Пусть это будет образ `phpmyadmin` (графический интерфейс для управдения базами данных) и БД `mysql`.

![Снимок экрана от 2024-11-25 12-27-17](https://github.com/user-attachments/assets/a7349cf8-be15-40ec-96ad-326f5c1cc248)

![Снимок экрана от 2024-11-25 12-27-42](https://github.com/user-attachments/assets/3627cb78-6186-49bd-810f-755bf6602467)

* Ниже напишем Docker Compose файл с описанием выше упомянутых сервисов и нашим проектом.

```
version: '3.1'

services:
  php: 
    build: ./php
    ports:
      - 8081:80

  db:
    image: mysql
    restart: always
    command: --default-authentication-plugin=mysql_native_password
    environment:
      MYSQL_ROOT_PASSWORD: 12345678
    ports:
      - 3030:3030

  phpmyadmin:
    image: phpmyadmin
    restart: always
    ports:
      - 8080:80
    environment:
      - PMA_ARBITRARY=1
```

* `build: ./php` - явно указываем где находится Dockerfile со всеми настройками проекта.

* Давайте соберем и запустим наш Docker Compose файл
* `sudo docker compose build` - собрать проект.
* `sudo docker compose up` - запустить проект.

![image](https://github.com/user-attachments/assets/45980189-5e44-495c-adc4-8eb1862b97fd)

![Снимок экрана от 2024-11-25 13-08-24](https://github.com/user-attachments/assets/b6965f7e-fbb3-4c7a-9b64-cc662439e8b5)

![image](https://github.com/user-attachments/assets/89e9e931-81f1-4c0d-a3b3-1270d13620d8)


![Снимок экрана от 2024-11-25 13-08-40](https://github.com/user-attachments/assets/7cb3e5ff-2e31-4746-b7c4-4f8a2c4ccc45)

* Как можно увидеть у нас все запустилось. Но у нас не получается подключиться в phpmyadmin. Эту проблему мы решим дальше.

## Хороший Docker Compose

```
version: '3.2'

services:
  php: 
    build: ./php
    ports:
      - 8081:80
    networks:
      - app_network

  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root_password
    networks:
      - db_network

  phpmyadmin:
    image: phpmyadmin:5.2
    restart: always
    ports:
      - 8080:80
    environment:
      PMA_HOST: db
      PMA_USER: root
      PMA_PASSWORD: root_password
    networks:
      - db_network

networks:
  db_network:
    name: db_network
    driver: bridge
  app_network:
    name: app_network
    driver: bridge
```

* Так будет выглядеть наш исправленный **docker-compose.yml**. Давайте запустим его и убедимся, что все работает.
* `sudo docker compose build` - собрать проект.
* `sudo docker compose up` - запустить проект.

![Снимок экрана от 2024-12-15 14-20-09](https://github.com/user-attachments/assets/fdfbe765-ae71-4d54-bf5a-721bd5828884)

![Снимок экрана от 2024-12-15 14-27-15](https://github.com/user-attachments/assets/421edaf0-e9df-420e-b3fc-f2ea4db5a790)

* Как видим все заработало. Давайте сделаем наш **docker-compose.yml** еще лучше и вынесем переменные окружения в отдельный файл `.env`.
* Для этого создадим в папке с нашим проектом файл **.env** и заполним его.

![Снимок экрана от 2024-12-15 15-42-54](https://github.com/user-attachments/assets/e58826b0-91c7-4185-bcf9-86e7efb5f3cc)

* Также чуть перепишем наш docker-compose-файл.

```
version: '3.2'

services:
  php: 
    build: ./php
    ports:
      - 8081:80
    networks:
      - app_network

  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    networks:
      - db_network

  phpmyadmin:
    image: phpmyadmin:5.2
    restart: always
    ports:
      - 8080:80
    environment:
      PMA_HOST: ${PMA_HOST}
      PMA_USER: ${PMA_USER}
      PMA_PASSWORD: ${PMA_PASSWORD}
    networks:
      - db_network

networks:
  db_network:
    name: db_network
    driver: bridge
  app_network:
    name: app_network
    driver: bridge
```

* Собираем проект заново и проверяем, что все заработало.

![Снимок экрана от 2024-12-15 15-43-45](https://github.com/user-attachments/assets/54092acd-60e7-474c-945b-c7b946d6ca3e)

![Снимок экрана от 2024-12-15 15-43-53](https://github.com/user-attachments/assets/b8c479b1-8780-4ea7-80d9-129deeb171a6)

* Что поменялось:
1. Первая плохая практика, которую мы исправили - это хранение переменных окружения в явном виде. Например: `MYSQL_ROOT_PASSWORD: 12345678`. В хорошем **docker-compose** файле мы подставляем значения переменных окружения из файла `.env`. Что нам это дает? Этим действием мы повышаем безопасность. Также упрощаем сам процесс разработки, ведь файл `.env` позволяет централизованно управлять переменными окружения, избегая необходимости редактировать сам файл `docker-compose.yml`. Для разных разработчиков или окружений можно иметь свои версии `.env` (например, `.env.local`, `.env.dev`, `.env.prod`).
2. Второй плохой практикой является то, что мы не указывали версии используемых нами образов. Мы все еще работает с Docker, поэтому не забываем о том, что отсутствие тегов образов может привести к непредсказуемому поведению нашего проекта.
3. Также в наш хороший **docker-compose** фалй мы использовали изолированные сети для разделения различных сервисов на логические сегменты. Таким образом, сервис `php` с нашим приложением работал в своей сети - **app_network**, а `bd` и `phpmyadmin` - **db_network**. Изоляция сервисов в разные сети в **Docker Compose** имеет несколько важных преимуществ: 
изолируя базы данных и административные инструменты (например, `phpmyadmin`) от других сервисов, мы минимизируем риски. Например, если сервис php скомпрометирован, злоумышленник не сможет сразу получить доступ к базе данных, так как она находится в отдельной сети. База данных (в нашем случае `db`) не будет доступна для других контейнеров, которые не должны взаимодействовать с ней. Это ограничивает возможности несанкционированного доступа. Также стоит отметить что когда контейнеры подключены к разным сетям, они могут использовать одинаковые порты внутри каждой сети, поскольку сеть изолирует контейнеры друг от друга. В кратце, изоляция сервисов в разные сети — это хорошая практика, которая помогает повысить безопасность, улучшить управляемость и уменьшить вероятность конфликтов между контейнерами. 
