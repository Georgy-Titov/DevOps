# Лабораторная работа по Docker (Advanced-трек)

- [Задание](#задание)
- [Подготовка окружения](#подготовка-окружения)
- [Файл конфигурации](#файл-конфигурации)
- [Скрипт](#Скрипт)
- [Проверка работоспосбности](#проверка-работоспосбности)
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

Рассмотрим ключевые функции скрипта `run-mini-container.py`. Скрипт реализует базовый контейнерный runtime и выполняет:

* создание overlayfs
* создание namespaces
* chroot
* монтирование файловых систем
* запуск процесса контейнера

Функция `load_config()` отвечает за загрузку конфигурационного файла контейнера.

```
def load_config():
    log_info("Загрузка конфигурации config.json")
    with open("config.json") as f:
        return json.load(f)
```

Функция `create_container_dirs()` создаёт структуру контейнера.

```
def create_container_dirs(container_id):
  container_path = os.path.join(BASE_DIR, container_id)

  ...

  os.makedirs(upper, exist_ok=True)
  os.makedirs(work, exist_ok=True)
  os.makedirs(merged, exist_ok=True)
```

Функция `setup_overlay()` создаёт файловую систему контейнера.

```
def setup_overlay(container_path, lowerdir):
  upperdir = os.path.join(container_path, "upper")
  workdir = os.path.join(container_path, "work")
  merged = os.path.join(container_path, "merged")

  ...

  lowerdir = os.path.abspath(lowerdir)

  ...

  mount_cmd = [
    "mount",
    "-t", "overlay",
    "overlay",
    "-o", f"lowerdir={lowerdir},upperdir={upperdir},workdir={workdir}",
    merged
]
```

Функция `mount_filesystems()` монтирует файловые системы из config.json.

```
def mount_filesystems(config):
  mounts = config.get("mounts", [])

  ...

  subprocess.run([
    "mount",
    "-t",
    fs_type,
    source,
    destination
], check=True)
```

Функция `build_unshare_command()` формирует команду unshare.

```
def build_unshare_command(config):
  namespaces = config["linux"]["namespaces"]

  ...

  if ns_type == "pid":
    cmd.append("--pid")

  # В итоге формируется команда: unshare --fork --pid --mount --uts
```

Функция `run_container()` запускает контейнер.

```
def run_container(rootfs, config)

# Установка hostname:
setup_hostname(config)

# Chroot:
os.chroot(rootfs)
os.chdir("/")

# Контейнер получает собственную файловую систему.
# Монтирование файловых систем:
mount_filesystems(config)

# Получение команды запуска:
cmd = config["process"]["args"]

# Получение переменных окружения:
env = build_env(config)

# Запуск процесса контейнера:
os.execvpe(cmd[0], cmd, env)

# Данный процесс становится PID=1 внутри контейнера.
```

Функция `main()` управляет запуском контейнера.

```
# Проверка аргументов:
if len(sys.argv) < 3:

# Режим run:
if command == "run":

# Создание overlayfs:
rootfs = setup_overlay(container_path, rootfs_path)

# Создание namespaces:
unshare_cmd = build_unshare_command(config)

# Запуск контейнера:
subprocess.run(
    unshare_cmd + [
        "python3",
        __file__,
        "child",
        rootfs
    ],
    check=True
)

# Режим child:
elif command == "child":

#Запуск контейнера:
run_container(rootfs, config)
```

## Проверка работоспосбности

Запустим наш "контейнер" командой `python3 run-mini-container.py run container-1`:

<img width="1276" height="536" alt="image" src="https://github.com/user-attachments/assets/dd7dbd73-d90c-43d1-8d37-842f00c653e2" />

Внутри контейнера основной процесс (`/bin/sh`) должен быть PID=1, так как он является init-процессом контейнера.

<img width="499" height="89" alt="Снимок экрана 2026-03-31 в 03 59 47" src="https://github.com/user-attachments/assets/f86e1183-8647-4718-9408-bb24bb7eadb7" />

Проверка `hostname`:

<img width="131" height="61" alt="Снимок экрана 2026-03-31 в 04 07 26" src="https://github.com/user-attachments/assets/1848aa84-c6a6-49c8-8eca-291f23bfb726" />

Проверка работы файловой системы:

<img width="421" height="334" alt="Снимок экрана 2026-03-31 в 04 02 28" src="https://github.com/user-attachments/assets/1a996626-1dc2-41f9-89a0-b144b9807933" />

Проверяем что в rootfs изменения не сохранились:

<img width="440" height="247" alt="Снимок экрана 2026-03-31 в 04 02 46" src="https://github.com/user-attachments/assets/864766b8-2eef-4590-84f3-6741faf8f1b1" />

А в merged изменения сохранились:

<img width="430" height="363" alt="Снимок экрана 2026-03-31 в 04 03 44" src="https://github.com/user-attachments/assets/ed3dc0ee-f232-450c-a07a-15e8c4c6e6c7" />

## Выводы

