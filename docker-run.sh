#!/bin/bash

# Скрипт запуска Docker контейнеров для 3proxy Manager

echo "🚀 Запуск 3proxy Manager в Docker..."

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose не установлен. Установите docker-compose и попробуйте снова."
    exit 1
fi

# Останавливаем существующие контейнеры
echo "🛑 Остановка существующих контейнеров..."
docker-compose down

# Запускаем контейнеры
echo "🐳 Запуск контейнеров..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ Контейнеры успешно запущены!"
    echo ""
    echo "🌐 Веб-интерфейс: http://localhost:5000"
    echo "🔐 Логин: admin, Пароль: admin123"
    echo "🌍 Прокси: localhost:3128"
    echo ""
    echo "📋 Полезные команды:"
    echo "  docker-compose logs -f          # Просмотр логов"
    echo "  docker-compose ps               # Статус контейнеров"
    echo "  docker-compose down             # Остановка контейнеров"
    echo "  docker-compose restart          # Перезапуск контейнеров"
else
    echo "❌ Ошибка при запуске контейнеров"
    exit 1
fi
