# Лабораторная работа №3

- [Задание](#задание)
- [Теория](#теория)
- [Устанвока инструментов](#установка-инструментов)
- [Создание приложения](#создание-приложения)
- [Запуск кластера](#запуск-кластера)
- [Тестируем](#тестируем)
- ["BAD PRACTICES" в работе с контейнерами]("bad-practices"-в-работе-с-контейнерами)
- [Выводы](#выводы)

## Задание: 

Поднять kubernetes кластер локально (например minikube), в нём развернуть свой сервис, используя 2-3 ресурса kubernetes. В идеале разворачивать кодом из yaml файлов одной командой запуска. Показать работоспособность сервиса.

## Теория

![image](https://github.com/user-attachments/assets/7f76e69e-d349-41a6-b8dd-40e44bae0668)

Kubernetes (k8s) — это платформа с открытым исходным кодом для автоматизации развертывания, масштабирования и управления контейнеризованными приложениями. Основная задача Kubernetes — упростить эксплуатацию большого количества контейнеров (сотни, тысячи контейнеров), решая такие задачи, как:

* Автоматическом развертывании приложений в контейнерах на разных серверах;
* Распределении нагрузки по нескольким серверам;
* Автоматическом масштабировании развернутых приложений;
* Мониторинге и проверке работоспособности контейнеров;
* Замене нерабочих контейнеров;

Составляющие части кластра Kubernetes:

![image](https://github.com/user-attachments/assets/113cbb9a-9245-408d-9d65-d60591349863)

Master Node (Control plane):

* API Server - по сути это наш способ взаимодействия с кластером. Если нужно что-то сделать, то запрос идет в этот компонент.

* Controller Manager - роль этого джентльмена в наблюдении за всем кластером, проверке все ли в порядке, а если что-то не так - ему надо принимать меры. У Controller Manager есть план, которого все в кластере должны придерживаться - такой план называется “Желаемое состояние” (desired state), то есть то, как все должно работать в идеале, и задача контроллера всегда приводить текущее состояние (current state) к желаемому.

* Scheduler - планирует то, как расположить контейнеры на различных нодах кластера в зависимости от различных факторов, таких как загруженность ноды и доступность серверных мощностей на ней.

* etcd - это хранилище данных в виде ключ-значение (key-value). Здесь хранится важная информация, которая отражает текущее состояние кластера: конфигурационные данные, статусы наших нод и контейнеров ну и так далее.

Worker Node (Data plane):

* kubelet - он отвечает за общение с мастером, получая инструкции что и как должно работать на этой конкретной ноде.

* container runtime - отвечает за образы контейнеров, их запуск и остановку, а также управление их ресурсами.

* kube-proxy - он выполняет сетевую роль - отвечает за коммуникацию и балансировку внутренней сети.

POD - это наименьшая и базовая единица развертывания. Он представляет собой абстракцию над одним или несколькими контейнерами, которые работают на одном узле, имеют общий сетевой стек (IP-адрес, порты), могут использовать общие тома (файловую систему), запускаются и управляются как единое целое.

[Источник](https://www.youtube.com/watch?v=klmpiHLSuXA&ab_channel=MerionAcademy)

> Также об инструментах, которые будут использованы для выполнения лабораторной работы.

* Minikube — это инструмент для запуска локального Kubernetes-кластера.
* kubectl — это CLI (интерфейс командной строки) для управления Kubernetes-кластером (включая кластер, созданный Minikube)

## Установка инструментов

* Подробнее ознакомиться с установкой можно [здесь](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fwindows%2Fx86-64%2Fstable%2F.exe+download)(Minikube) и [здесь](https://kubernetes.io/docs/tasks/tools/)(kubectl). Мы же воспользуемся следующими командами:

* Для установки kubectl:

```
sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
```

![image](https://github.com/user-attachments/assets/1a0db47f-c1b0-465b-8123-ade2f0638df5)

* Для Minikube:

```
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
```

![image](https://github.com/user-attachments/assets/22eec222-6e1a-4924-ae63-5d553b30a984)

## Создание приложения

* В качестве испытуемого у нас будет небольшое веб-приложение на Flask, которое будет выводить текущее время и приветсвенное предложение:

```
from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def hello_kubernetes():
    now = datetime.now()
    kubernetes_ascii = """
<pre>
              .-/+oossssoo+/-.              
          `:+ssssssssssssssssss+:`          
        -+ssssssssssssssssssyyssss+-        
      .ossssssssssssssssssdMMMNysssso.      
     /ssssssssssshdmmNNmmyNMMMMhssssss/     
   +ssssssssshmydMMMMMMMNddddyssssssss+     
  /sssssssshNMMMyhhyyyyhmNMMMNhssssssss/    
 .ssssssssdMMMNhsssssssssshNMMMdssssssss.   
 +sssshhhyNMMNyssssssssssssyNMMMysssssss+   
 ossyNMMMNyMMhsssssssssssssshmmmhssssssso   
 ossyNMMMNyMMhsssssssssssssshmmmhssssssso   
 +sssshhhyNMMNyssssssssssssyNMMMysssssss+   
 .ssssssssdMMMNhsssssssssshNMMMdssssssss.   
  /sssssssshNMMMyhhyyyyhdNMMMNhssssssss/    
   +sssssssssdmydMMMMMMMMddddyssssssss+     
     /ssssssssssshdmNNNNmyNMMMMhssssss/     
      .ossssssssssssssssssdMMMNysssso.      
        -+sssssssssssssssssyyyssss+-        
          `:+ssssssssssssssssss+:`          
              .-/+oossssoo+/-.
</pre>
"""
    return f"""
    <h1>Hello, It's Kubernetes</h1>
    <p>Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
    {kubernetes_ascii}
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

```

* Также добавим файл со всеми необходимыми зависимостями. Они нам понадобятся на этапе создания образа:

```
#requirements.txt
Flask==2.0.1
Werkzeug==2.0.3
```

* Dockerfile:

```
#Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY python-app.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "python-app.py"] 
```

* Собираем наш образ:

```
sudo docker build -t python-flask-app:1.0 .
```

## Запуск кластера


