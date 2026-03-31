# Лабораторная работа по Docker (Advanced-трек)

- [Задание](#задание)
- [Подготовка окружения](#подготовка-окружения)
- [Файл конфигурации](#файл-конфигурации)
- [Скрипт](#Скрипт)
- [Запуск кластера](#запуск-кластера)
- [Тестируем](#тестируем)
- [Выводы](#выводы)

## Задание: 

Разработайте утилиту на любом удобном языке программирования (например, Go, Python), которая запускает команду в контейнере.

1. Должна конфигурироваться config.json по спецификации OCI
2. Для каждого контейнера при его запуске должны создаваться новые namespaces:
   * PID namespace;
    * Mount namespace;
    * UTS namespace, внутри которого hostname устанавливается в значение из поля hostname конфига.
3. Для каждого контейнера с идентификатором <id> должна создаваться директория: /var/lib/{имя-вашей-утилиты}/{id}
4. В качестве rootfs использовать Alpine, но chroot делать на overlayfs:
    * lowerdir — базовый rootfs (Alpine)
    * upperdir — /var/lib/{имя-утилиты}/{id}/upper
    * workdir — /var/lib/{имя-утилиты}/{id}/work
    * merged - /var/lib/{имя-утилиты}/{id}/merged
5. Запускаемая команда становится PID=1 внутри контейнера и утилита ждёт её завершения (foreground)

Опционально:
1) Настроить cgroups для ограничения ресурсов контейнера (CPU, память, IO).
2) Внутри контейнера монтировать /proc для корректной работы утилит типа ps

## Подготовка окружения

Работа выполнялась на удалённом сервере (VPS). Для удобства работы был настроен SSH-доступ к серверу, после чего была создана рабочая директория проекта. Стурктур проекта будет иметь следующий вид:

```
~/Documents/DevOps-labs/Docker-lab1$ tree -L 1
.
├── config.json              # конфигурационный файл контейнера
├── rootfs                   # базовая файловая система контейнера (Alpine Linux)
└── run-mini-container.py    # скрипт запуска контейнера
```

После был скачан минимальный образ файловой системы [Alpine Linux](https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/) (rootfs). Для лабораторной работы была использована актуальная стабильная версия Alpine Linux 3.23.3.

Скачивание rootfs выполнялось следующими командами:

```
wget https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/alpine-minirootfs-3.23.3-x86_64.tar.gz
mkdir rootfs
tar -xzf alpine-minirootfs-3.23.3-x86_64.tar.gz -C rootfs
```

<img width="424" height="317" alt="Снимок экрана 2026-03-31 в 02 53 14" src="https://github.com/user-attachments/assets/21e1dc1c-115d-468d-b9b8-fffec75a9365" />

## Файл конфигурации

Для настройки параметров запуска контейнера используется файл `config.json`.
Он описывает поведение контейнера и его окружение. Формат конфигурации основан на спецификации **Open Container Initiative** ([OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)).

Рассмотрим ключевые блкои в файле конфигурации:

```
{
  "ociVersion": "1.0.2",
  "hostname": "mini-container",
  "process": {
    "terminal": true,
    "user": {
      "uid": 0,
      "gid": 0
    },
    "args": [
    "/bin/sh",
    "-c",
    "echo '<<mini-container started successfully!>>'; exec /bin/sh -i"
    ],
    "env": [
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    ],
    "cwd": "/"
  },
  "root": {
    "path": "rootfs",
    "readonly": false
  },
  "mounts": [
    {
      "destination": "/proc",
      "type": "proc",
      "source": "proc"
    },
    {
      "destination": "/dev",
      "type": "tmpfs",
      "source": "tmpfs"
    },
    {
      "destination": "/sys",
      "type": "sysfs",
      "source": "sysfs"
    }
  ],
  "linux": {
    "namespaces": [
      {
        "type": "pid"
      },
      {
        "type": "mount"
      },
      {
        "type": "uts"
      }
    ],
    "resources": {
      "memory": {
        "limit": 268435456
      },
      "cpu": {
        "shares": 1024
      }
    }
  }
}
```

##

```
"ociVersion": "1.0.2"
```

Указывает версию спецификации OCI, используемой для описания контейнера.

```
"hostname": "mini-container"
```

Задает имя хоста внутри контейнера. Благодаря namespace UTS контейнер получает собственное имя хоста, независимое от основной системы.

```
"process": {
  "terminal": true,      # Указывает, что контейнер запускается в интерактивном режиме с терминалом.
  "user": {              # Указывает пользователя, от имени которого запускается контейнер.
    "uid": 0,              В данном случае используется пользователь root (uid=0, gid=0).
    "gid": 0               В продакшене лучше так не делать)
  }
```

Блок `process` описывает основной процесс контейнера.

```
"args": [
  "/bin/sh",
  "-c",
  "echo '<<mini-container started successfully!>>'; exec /bin/sh -i"
]
```

Этот блок задает команду, которая будет запущена внутри контейнера. В нашем случае при старте контейнера выведется сообщение об его успешном запуске и управление перейдет в интерактивном режиме оболочке `/bin/sh`.

```
{
  "destination": "/proc",
  "type": "proc",
  "source": "proc"
}
```

Монтирует виртуальную файловую систему `/proc`, которая содержит информацию о процессах.

```
{
  "destination": "/dev",
  "type": "tmpfs",
  "source": "tmpfs"
}
```

Монтирует временную файловую систему `/dev,` содержащую устройства контейнера.

```
{
  "destination": "/sys",
  "type": "sysfs",
  "source": "sysfs"
}
```

Монтирует `/sys`, содержащую информацию о системе и ядре.


```
"namespaces": [
  { "type": "pid" },      # pid	изоляция процессов
  { "type": "mount" },    # mount	изоляция файловой системы
  { "type": "uts" }       # uts	отдельный hostname
]
```

Используются namespaces для изоляции контейнера.

```
"memory": {
  "limit": 268435456
}

...

"cpu": {
  "shares": 1024
}

```

Ограничение ресурсов (cgroups).

## Скрипт
