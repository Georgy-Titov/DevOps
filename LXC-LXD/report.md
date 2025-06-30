# LXC/LXD контейнеризация 

- [Задание](#задание)
- [Теория](#теория)
- [Выполнение задания](#выполнение-задания)
- [Конфигурация Terraform и Yandex Cloud](#конфигурация-terraform-и-yandex-cloud)
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

```
sudo lxc launch <нужный образ> <имя контейнера>
# В нашем случае -->  sudo lxc launch ubuntu:22.04 ubuntu-nginx

# Посмотреть доступны образы можно при помощи команды:
lxc image list images:
```

* Проверяем что контейнр запустился:

```
lxc list
```

* Подключаемся к контейнеру и устанваливаем Nginx:

```
```




