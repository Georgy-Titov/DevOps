# LXC/LXD контейнеризация 

- [Задание](#задание)
- [Теория](#теория)
- [Выполнение задания](#выполнение-задания)
- [Выводы](#выводы)

## Задание: 

Получить практические навыки работы с LXD для управления контейнерами, настройкой сетевых мостов, проброса портов и развертывания веб-приложений (на примере nginx).

## Теория

![image](https://github.com/user-attachments/assets/5d135904-86d7-48b4-884b-b7245ecab169)

* **LXC (Linux Containers)** — это технология контейнеризации на уровне ОС, которая использует возможности ядра Linux (cgroups, namespaces и др) для создания изолированных окружений (контейнеров).

* **LXD (Linux Container Daemon)** — это надстройка над LXC, которая:
  * Упрощает управление контейнерами (через REST API, cli-инструмент `lxc`);
  * Добавляет управление образами, профилями, снапшотами, сетями, storage и др;
  * Делает работу с контейнерами похожей на работу с виртуальными машинами (но без hypervisor).

* Основные компоненты:
  * LXD Daemon (lxd) - фоновый сервис, который управляет контейнерами;
  * CLI клиент (lxc) - командная строка для взаимодействия с LXD;
  * Storage pools	- хранилища для контейнеров и образов (zfs, btrfs, dir, lvm).
  * Networks / bridges - виртуальные сети, мосты, NAT для контейнеров.
  * Profiles - наборы настроек (например, подключённые устройства, сети).
  * Containers / VMs - контейнеры LXC или виртуалки (LXD поддерживает и то, и другое).
  * Images - образы контейнеров для развертывания новых экземпляров.

## Выполнение задания

* Устанавливаем LXD:

```
sudo snap install lxd
sudo lxd init
```

* Команда `lxd init` запустит интерактивный мастер, который будет задавать вопросы о базовой конфигурации LXD:

```
# Конфигурация:
Would you like to use LXD clustering? (yes/no) [default=no]: no
Do you want to configure a new storage pool? (yes/no) [default=yes]: yes
Name of the new storage pool [default=default]: lxc-lxd-lab-pool
Name of the storage backend to use (powerflex, zfs, btrfs, ceph, dir, lvm) [default=zfs]: zfs
Create a new ZFS pool? (yes/no) [default=yes]: yes
Would you like to use an existing empty block device (e.g. a disk or partition)? (yes/no) [default=no]: no
Size in GiB of the new loop device (1GiB minimum) [default=30GiB]: 5GiB
Would you like to connect to a MAAS server? (yes/no) [default=no]: no
Would you like to create a new local network bridge? (yes/no) [default=yes]: yes
What should the new bridge be called? [default=lxdbr0]: 
What IPv4 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]: 
What IPv6 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]: 
Would you like the LXD server to be available over the network? (yes/no) [default=no]: no
Would you like stale cached images to be updated automatically? (yes/no) [default=yes]: yes
```

* Далее создадим и запустим котнейнер при помощи команды:

> Если во время выполнения команд у вас появляются ошибки типа "permission denied" - добавьте вашего пользоватся в группу lxd. `sudo usermod -aG lxd $USER`.

```
lxc launch <нужный образ> <имя контейнера>
# В нашем случае -->  lxc launch ubuntu:22.04 ubuntu-nginx

# Посмотреть доступные образы можно при помощи команды:
lxc image list images:
```

* Проверяем что контейнр запустился:

```
lxc list

# Вывод команды
+-----------+---------+-----------------------+-----------------------------------------------+-----------+-----------+
|   NAME    |  STATE  |         IPV4          |                     IPV6                      |   TYPE    | SNAPSHOTS |
+-----------+---------+-----------------------+-----------------------------------------------+-----------+-----------+
| webserver | RUNNING | 10.146.142.148 (eth0) | fd42:3bf0:c2dd:e516:216:3eff:fee1:5c19 (eth0) | CONTAINER | 0         |
+-----------+---------+-----------------------+-----------------------------------------------+-----------+-----------+
```

* Подключаемся к контейнеру и устанваливаем Nginx:

```
lxc shell webserver

apt update
apt install nginx -y
systemctl start nginx

#####################################

На этом шаге у вас могла возникнуть проблема с тем, что изнутри контейнера не было доступа в интернет.
Даже если у вас правильно настроены мост, DNS и NAT.
Одно из решений данной проблемы - включение маршрутизации (FORWARDING) для трафика между контейнерным интерфейсом и внешним.

```

* Проверяем что Nginx устанвился сначала внутри контейнера - `curl http://127.0.0.1`

![image](https://github.com/user-attachments/assets/14102838-e0c5-450b-8be2-e268135cea37)

* Далее при помощи `proxy` пробрасываем порт контейнера на локальный хост. Теперь любые запросы (0.0.0.0:8080) на порт 8080 будут перенаправляться в контейнер на адрес 127.0.0.1:80.

```
lxc config device add webserver myport80 proxy listen=tcp:0.0.0.0:8080 connect=tcp:127.0.0.1:80
```

* Проверяем доступ на локальном хосте:

![image](https://github.com/user-attachments/assets/cf266560-637d-4a9b-b08e-7b4afde7f64c)

* Опять на локальном хосте только в браузере:

![image](https://github.com/user-attachments/assets/e47beb15-ed95-4ef3-9d13-c749a973f961)

* Также попробуем подключиться с другого устройства в моей домашней сети. Посмотреть Ip-адрес устройства можно при помощи команды `ifconfig` или `ip a`. 

![image](https://github.com/user-attachments/assets/ac38ea6e-6381-41ea-9a7d-667570e3d261)

## Выводы

В ходе лабораторной работы были получены практические навыки установки и настройки LXD для контейнеризации. Я научился создавать контейнеры, подключаться к ним и управлять их жизненным циклом. Особое внимание было уделено настройке сетевой инфраструктуры: созданию мостов, пробросу портов с хоста в контейнеры с помощью proxy-устройств, что позволило обеспечить доступ к запущенному в контейнере веб-серверу (nginx) как с локального хоста, так и с других устройств в сети.
