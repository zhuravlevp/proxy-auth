@echo off
REM Скрипт запуска Docker контейнеров для 3proxy Manager (Windows)

echo 🚀 Запуск 3proxy Manager в Docker...

REM Проверяем наличие docker-compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ docker-compose не установлен. Установите docker-compose и попробуйте снова.
    pause
    exit /b 1
)

REM Останавливаем существующие контейнеры
echo 🛑 Остановка существующих контейнеров...
docker-compose down

REM Запускаем контейнеры
echo 🐳 Запуск контейнеров...
docker-compose up -d

if errorlevel 0 (
    echo ✅ Контейнеры успешно запущены!
    echo.
    echo 🌐 Веб-интерфейс: http://localhost:5000
    echo 🔐 Логин: admin, Пароль: admin123
    echo 🌍 Прокси: localhost:3128
    echo.
    echo 📋 Полезные команды:
    echo   docker-compose logs -f          # Просмотр логов
    echo   docker-compose ps               # Статус контейнеров
    echo   docker-compose down             # Остановка контейнеров
    echo   docker-compose restart          # Перезапуск контейнеров
) else (
    echo ❌ Ошибка при запуске контейнеров
    pause
    exit /b 1
fi

pause
