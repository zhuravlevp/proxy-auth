# Docker контейнеризация 3proxy Manager

## 🐳 Обзор

Проект полностью контейнеризован с использованием Docker и docker-compose для удобного развертывания и управления.

## 📁 Структура Docker файлов

```
auth-proxy/
├── Dockerfile              # Основной Dockerfile для Python приложения
├── docker-compose.yml      # Конфигурация всех сервисов
├── .dockerignore           # Исключения для Docker build
├── docker-build.sh         # Скрипт сборки (Linux/Mac)
├── docker-build.bat        # Скрипт сборки (Windows)
├── docker-run.sh           # Скрипт запуска (Linux/Mac)
├── docker-run.bat          # Скрипт запуска (Windows)
└── nginx/
    └── nginx.conf          # Конфигурация Nginx reverse proxy
```

## 🚀 Быстрый старт

### 1. Сборка и запуск (автоматически)

#### Linux/Mac:
```bash
# Сборка
chmod +x docker-build.sh
./docker-build.sh

# Запуск
chmod +x docker-run.sh
./docker-run.sh
```

#### Windows:
```cmd
# Сборка
docker-build.bat

# Запуск
docker-run.bat
```

### 2. Ручная сборка и запуск

```bash
# Сборка образа
docker build -t auth-proxy-manager:latest .

# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

## 🏗️ Архитектура

### Сервисы:

1. **auth-proxy** - Основное Python приложение
   - Порт: 5000
   - Веб-интерфейс управления 3proxy
   - API для Chrome расширения

2. **proxy-server** - 3proxy сервер
   - Порт: 3128
   - SOCKS5 прокси сервер
   - Автоматическая конфигурация

3. **nginx** - Reverse proxy (опционально)
   - Порт: 80, 443
   - SSL терминация
   - Балансировка нагрузки

## 🔧 Конфигурация

### Переменные окружения:

```yaml
environment:
  - FLASK_ENV=production
  - PYTHONUNBUFFERED=1
```

### Volumes:

- `./config:/app/config` - Конфигурационные файлы
- `./logs:/app/logs` - Логи приложения
- `./nginx/ssl:/etc/nginx/ssl` - SSL сертификаты

## 📋 Команды управления

### Основные команды:

```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Перезапуск сервисов
docker-compose restart

# Просмотр статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f auth-proxy
```

### Управление отдельными сервисами:

```bash
# Запуск только веб-приложения
docker-compose up -d auth-proxy

# Запуск только прокси сервера
docker-compose up -d proxy-server

# Перезапуск конкретного сервиса
docker-compose restart auth-proxy
```

## 🔍 Мониторинг и отладка

### Просмотр логов:

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f auth-proxy
docker-compose logs -f proxy-server
docker-compose logs -f nginx
```

### Подключение к контейнеру:

```bash
# Подключение к веб-приложению
docker-compose exec auth-proxy bash

# Подключение к прокси серверу
docker-compose exec proxy-server sh
```

### Проверка статуса:

```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Информация о сети
docker network ls
```

## 🔒 Безопасность

### SSL/TLS:

1. **Автоматическое создание сертификатов** для разработки
2. **Настройка Nginx** для SSL терминации
3. **Security headers** для защиты

### Пользователи:

- Приложение запускается под непривилегированным пользователем
- Изолированные контейнеры
- Ограниченные права доступа

## 🌐 Сетевые настройки

### Порты:

- **5000** - Веб-интерфейс 3proxy Manager
- **3128** - SOCKS5 прокси сервер
- **80** - HTTP (редирект на HTTPS)
- **443** - HTTPS (через Nginx)

### Доступ:

- **Веб-интерфейс**: http://localhost:5000
- **Прокси**: localhost:3128
- **Логин**: admin / admin123

## 📊 Производительность

### Оптимизации:

1. **Многоэтапная сборка** Docker образа
2. **Кэширование зависимостей** Python
3. **Минимальный базовый образ** (python:3.11-slim)
4. **Оптимизированные Nginx** настройки

### Мониторинг ресурсов:

```bash
# Использование ресурсов
docker stats

# Информация о контейнерах
docker-compose ps
```

## 🛠️ Разработка

### Локальная разработка:

```bash
# Запуск в режиме разработки
docker-compose -f docker-compose.dev.yml up -d

# Пересборка после изменений
docker-compose build --no-cache
docker-compose up -d
```

### Отладка:

```bash
# Подключение к контейнеру для отладки
docker-compose exec auth-proxy bash

# Просмотр конфигурации
docker-compose config

# Проверка синтаксиса
docker-compose config --quiet
```

## 🚀 Продакшен

### Рекомендации для продакшена:

1. **Используйте собственные SSL сертификаты**
2. **Настройте мониторинг** (Prometheus, Grafana)
3. **Настройте логирование** (ELK Stack)
4. **Используйте секреты** для паролей
5. **Настройте резервное копирование**

### Пример продакшен конфигурации:

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  auth-proxy:
    image: auth-proxy-manager:latest
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    secrets:
      - db_password
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

## 📝 Troubleshooting

### Частые проблемы:

1. **Порт уже используется**
   ```bash
   # Проверка занятых портов
   netstat -tulpn | grep :5000
   
   # Остановка конфликтующих сервисов
   sudo systemctl stop apache2
   ```

2. **Ошибки сборки**
   ```bash
   # Очистка кэша Docker
   docker system prune -a
   
   # Пересборка без кэша
   docker-compose build --no-cache
   ```

3. **Проблемы с сетью**
   ```bash
   # Пересоздание сети
   docker-compose down
   docker network prune
   docker-compose up -d
   ```

### Полезные команды:

```bash
# Очистка всех неиспользуемых ресурсов
docker system prune -a

# Просмотр использования места
docker system df

# Информация о системе
docker system info
```

## 📚 Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [3proxy Documentation](http://3proxy.ru/)
- [Flask Documentation](https://flask.palletsprojects.com/)
