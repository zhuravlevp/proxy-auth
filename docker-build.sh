#!/bin/bash

# Скрипт сборки Docker контейнера для 3proxy Manager

echo "🐳 Сборка Docker контейнера для 3proxy Manager..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose не установлен. Установите docker-compose и попробуйте снова."
    exit 1
fi

# Создаем необходимые директории
echo "📁 Создание директорий..."
mkdir -p config logs nginx/ssl

# Создаем самоподписанный SSL сертификат для разработки
if [ ! -f nginx/ssl/cert.pem ]; then
    echo "🔐 Создание SSL сертификата для разработки..."
    openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes -subj "/C=RU/ST=Moscow/L=Moscow/O=3proxy Manager/CN=localhost"
fi

# Собираем образ
echo "🔨 Сборка Docker образа..."
docker build -t auth-proxy-manager:latest .

if [ $? -eq 0 ]; then
    echo "✅ Образ успешно собран!"
    echo "🚀 Для запуска используйте: docker-compose up -d"
else
    echo "❌ Ошибка при сборке образа"
    exit 1
fi
