# Знакомство с Terraform

- [Задание](#задание)
- [Теория](#теория)
- [Установка инструментов](#установка-инструментов)
- [Конфигурация Terraform и Yandex Cloud](#конфигурация-terraform-и-yandex-cloud)
- [Выводы](#выводы)

## Задание: 

Ознакомиться с инструментом Terraform и принципами описания инфраструктуры в виде кода (Infrastructure as Code). Создать инфраструктуру в Yandex Cloud и запустить на виртуальной машине nginx с помощью Docker.

## Теория

> Подробно останавливаться на Best practices по работе с Terraform в данной работе не будем, так как у нас цель познакомиться с инструментом.

![image](https://github.com/user-attachments/assets/efd2f6ef-1204-4cfd-9a9f-ce46ae3d625e)

* **Terraform** — это инструмент для описания и управления инфраструктурой в виде кода (Infrastructure as Code, IaC). Он позволяет создавать, изменять и удалять ресурсы в облачных провайдерах (например, Yandex Cloud, AWS, GCP) и других сервисах. Terraform использует декларативный подход: вы описываете, какой результат хотите получить, а не как его достичь.

* Для чего нужен Terraform:
  * Автоматизации создания инфраструктуры (виртуальные машины, сети, базы данных, балансировщики и т.д.);
  * Управления конфигурацией инфраструктуры в виде кода (легко хранить в Git, отслеживать изменения);
  * Повышения воспроизводимости и уменьшения числа ошибок при ручной настройке.

* Основные команды Terraform:
  * terraform `init` — инициализация рабочего каталога, загрузка провайдеров и модулей.
  * terraform `plan` — просмотр плана изменений без их применения.
  * terraform `apply` — применение конфигурации, создание или изменение инфраструктуры.
  * terraform `destroy` — удаление созданной инфраструктуры.
  * terraform `output` — вывод значений, определённых в блоках output.
  * terraform `fmt` — автоматическое форматирование кода по стандарту Terraform.
  * terraform `validate` — проверка конфигурационных файлов на синтаксические ошибки.
  * terraform `taint` — пометка ресурса для пересоздания при следующем apply.

* Структура Terraform:
  * Файлы с расширением `.tf` — конфигурационные файлы с описанием инфраструктуры.
  * Файлы с расширением `.tfvars` — файлы для задания значений переменных.
  * Файлы с расширением `.tfstate` — файлы состояния, где фиксируется текущее состояние инфраструктуры.
  * Файл `.terraform.lock.hcl` — фиксирует версии провайдеров и модулей для стабильного воспроизведения инфраструктуры.
  * Каталог `.terraform/` — содержит загруженные провайдеры, модули и служебные данные.
 
* Основные компоненты Terraform:
  * **Providers** — плагины для взаимодействия с конкретными платформами (например, Yandex Cloud, AWS).
  * **Resources** — реальные объекты инфраструктуры, которые Terraform создаёт и управляет ими (например, виртуальные машины, сети).
  * **Data Sources** — получение информации о внешних объектах, которые не управляются напрямую Terraform.
  * **Outputs** — вывод значений после создания инфраструктуры (например, публичный IP).
  * **Modules** — наборы конфигураций для переиспользования кода.
  * **Variables** — входные данные для конфигураций (например, имя ВМ, регион).
  * **Locals** — локальные переменные для упрощения выражений внутри конфигурации.

## Установка инструментов

* Нам понадобиться установить Terraform и Yandex Cloud CLI. Подробно останавливаться на устанвоке каждого из инструментов не будем, поэтому я прикреплю инструкции, по которым вы сможете выбрать удобный для себя способ установки:

 * Terraform - [HashiCorp](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli?in=terraform%2Faws-get-started) или [инструкция из интернета](https://timeweb.cloud/tutorials/cloud/ustanovka-terraform)
 * CLI [Yandex Cloud](https://yandex.cloud/ru/docs/cli/operations/install-cli)

![image](https://github.com/user-attachments/assets/31c2e347-bc25-4f4e-998c-717552d218e5)


* Также отметим что для выполнения работы потребуетсяс создать аккаунт в Yandex Cloud. Также после создания понадобиться завести платежный аккаунт для доступа к ресурсам провайдера. При создании первого платежного аккаутна вам выдается грант в 4000 руб. Этого достаточно для нашей работы.

* Также полезна будет следующая документация:
  * [Yandex Cloud Terraform](https://yandex.cloud/ru/docs/tutorials/infrastructure-management/terraform-quickstart#linux_1)
  * [Terraform Providers](https://registry.terraform.io/providers/yandex-cloud/yandex/latest/docs)

## Конфигурация Terraform и Yandex Cloud

* После того как все установили, открываем терминал и проводим начальную настройку CLI:

```
yc init

# CLI задаст вопросы:
# Войти через браузер и ввести OAuth токен (он откроется сам)
# Выбрать каталог (cloud)
# Выбрать папку (folder)

# cloud_id и folder_id можно посмотреть в веб-интерфейсе облака, либо получить при помощи слуедющмх команд:
# yc resource-manager cloud list
# yc resource-manager folder list
```

* После того как мы провели настройку CLI, перейдем к написанию `main.tf` - основной файл конфигурации (то что мы хотим получить):

```
terraform {
  required_providers {
    yandex = {
      source = "terraform-registry.storage.yandexcloud.net/yandex-cloud/yandex"
    }
  }
  required_version = ">= 0.13"
}

provider "yandex" {
  zone                     = "ru-central1-a"
  cloud_id                 = "b1gnl0qf3ceu8p4p0nfe"
  folder_id                = "b1gqr9fn97hptq8tr5e9"
  service_account_key_file = "key.json"
}

resource "yandex_vpc_network" "test-vpc" {
  name = "terraform-vpc"
}

resource "yandex_vpc_subnet" "test-subnet" {
  v4_cidr_blocks = ["10.2.0.0/16"]
  network_id     = yandex_vpc_network.test-vpc.id
}

resource "yandex_vpc_address" "test-addr" {
  name = "exampleAddress"

  external_ipv4_address {
    zone_id = "ru-central1-a"
  }
}

resource "yandex_compute_instance" "test-comp-inst" {
  name        = "test-comp-inst"
  platform_id = "standard-v3"

  resources {
    cores  = 2
    memory = 2
  }

  boot_disk {
    initialize_params {
      image_id = "fd82nvvtllmimo92uoul"
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.test-subnet.id
    nat = true
        nat_ip_address = yandex_vpc_address.test-addr.external_ipv4_address.0.address
  }

  metadata = {
    ssh-keys = "ubuntu:${file("/home/georgy/.ssh/id_rsa.pub")}"
    user-data = "${file("init.sh")}"
  }
}

output "external_ip" {
    value = yandex_vpc_address.test-addr.external_ipv4_address.0.address
}
```

* Вкратце разберем основные моменты:
  * Блок `terraform` указывает откуда брать провайдера и какую использовать версию Terraform;
  * Блок `provide` задает настройки для подключения к Yandex Cloud;
  * Ресурс `yandex_vpc_network` создает виртуальную сеть (VPC) в облаке;
  * Ресурс `yandex_vpc_subnet` создает подсеть внутри сети, которые мы объявили выше;
  * Ресурс `yandex_vpc_address` создает внешний IP-адрес для нашей будущей VM;
  * Ресурс `yandex_compute_instence` создает виртуальную машину;
  * Блок `output` нужен для получения внешнего IP-адреса после создания ресурса.
 
 * Далее про команды, которые были использованы в процессе написания конфигурационного файла:

```
# Запрашиваем список стандартных (готовых) образов виртуальных машин в Yandex Cloud. В данном примере ищем только образы Ubuntu
yc compute image list --folder-id standard-images | grep ubuntu

# Генерируем ssh-ключи для подключения к VM. Далее в конфиге передаем публичный ключ в metadata {ssh-keys = }
ssh-keygen -t rsa -b 4096 -f ./id_rsa
```

* Также мы передаем в `metadata {user-data}` мы передаем `"${file("init.sh")}"` - это скрипт, который будем исполнен при первом запуске VM. В скрипте мы устанавливаем Docker и запускаем контейнер с Nginx:

```
#!/bin/bash
# Обновление пакетов
apt-get update -y
apt-get upgrade -y

# Установка Docker
apt-get install -y docker.io

# Запуск Docker, если он не запущен
systemctl start docker
systemctl enable docker

# Скачивание и запуск Nginx в Docker
docker run -d --name nginx-container -p 80:80 nginx
```

![Снимок экрана от 2025-06-30 01-16-36](https://github.com/user-attachments/assets/276b503a-8c1b-4536-a16f-38845611b912)


![Снимок экрана от 2025-06-30 01-26-28](https://github.com/user-attachments/assets/4e8fbc8e-d5bf-44c5-abf4-e6bf7026f09e)

![image](https://github.com/user-attachments/assets/e00386cc-8ebd-49c5-8f59-f67494217af2)

