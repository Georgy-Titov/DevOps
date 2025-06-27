# Лабораторная работа №5

- [Задание](#задание)
- [Теория](#теория)
- [Предустановка](#предустановка)
- [Установка инструментов](#установка-инструментов)
- [Запуск кластера](#запуск-кластера)
- [Тестируем](#тестируем)
- [Выводы](#выводы)

## Задание: 

Сделать мониторинг сервиса, поднятого в кубере (использовать, например, prometheus и grafana). Показать хотя бы два рабочих графика, которые будут отражать состояние системы. Приложить скриншоты всего процесса настройки.

## Теория

**Prometheus** - это система мониторинга и оповещений с открытым исходным кодом, разработанная для сбора метрик с приложений и инфраструктуры.
Она особенно популярна для мониторинга микросервисов и кластеров Kubernetes благодаря своей гибкости и способности масштабироваться. Prometheus периодически (pull-модель) запрашивает метрики у приложений и сервисов в кластере. В нашем случае Prometheus будет опрашивать Flask-приложение, развернутое в Minikube, и собирать с него данные.

![image](https://github.com/user-attachments/assets/26d2a7e4-639b-4751-9f0d-043a211f45cd)

**Grafana** - это мощный инструмент для визуализации, анализа и мониторинга данных. Он позволяет строить красивые и наглядные дашборды (интерактивные панели с графиками и таблицами) на основе данных из разных источников (Prometheus, InfluxDB, Elasticsearch и др.). Grafana не собирает данные самостоятельно — она запрашивает их у Prometheus и строит графики на основе этих данных.

![image](https://github.com/user-attachments/assets/7641968a-2537-41b8-aa1e-785af3728255)

* В нашей лабораторной работе взаимодействие будет происходить следующим образом:
1. Prometheus подключается к нашему Flask-приложению, которое работает внутри Kubernetes (Minikube), и регулярно опрашивает его endpoint /metrics, чтобы собирать данные.
2. Эти данные сохраняются в базе данных Prometheus.
3. Grafana подключается к Prometheus как к источнику данных и получает собранные метрики.
4. В Grafana мы создаём дашборды с графиками, которые отображают текущее состояние системы (например, нагрузку на CPU, использование памяти, количество HTTP-запросов).

## Предустановка

> Перед тем как мы перейдем к установке нашего инструментария, сделаем пару модификаций нашего старого приложения:

* Сначала добавим пару строк в коде нашего Flask-приложения, а именно:

```
# Эта библиотека автоматически добавляет HTTP endpoint по адресу /metrics (его можно изменить, если нужно). 
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)
```

* Также обновляем наш файл requirements.txt:

```
Flask==2.0.1
Werkzeug==2.0.3
prometheus-flask-exporter==0.22.4
```

* Добавляем аннотацию в deployment.yaml:

```
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "5000"
```

* И собираем новый образ нашего приложения:

```
docker build -t python-flask-app:2.0 .
```

* Сам образ добавляем в minikube:

```
minikube image load python-flask-app:2.0

# Не забудьте также поменять образ приложения в deployment.yaml
```

* Это все нам надо, чтобы после того как мы установим Prometheus, он мог тянуть метрики не только с нашего кластера, но и самого приложения.

* Также давайте почистим базу etcd нашего кластера:

```
# Проверяем статус minikube
minikube starus

# Если не запущен, то запускаем
# minikube start

# Далее выполняем
kubectl delete deployment python-flask-app
kubectl delete service python-flask-app
```

* Далее запустим и проверим работу новой версии приложеия:

```
# Запускаем
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Проверяем что все запущено
kubectl get pods
kubectl get svc

# Открываем приложение в браузере
minikube service python-flask-app
```

![image](https://github.com/user-attachments/assets/f8af2bd0-651f-477e-8081-a71185fb26a5)


## Установка инструментов

* Начнем с установки Helm - пакетного менеджера для Kubernetes. Если проводить аналогии: Helm для K8s - apt для Ubuntu - pip для Python.

```
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```


