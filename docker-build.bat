@echo off
REM Скрипт сборки Docker контейнера для 3proxy Manager (Windows)

echo 🐳 Сборка Docker контейнера для 3proxy Manager...

REM Проверяем наличие Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не установлен. Установите Docker Desktop и попробуйте снова.
    pause
    exit /b 1
)

REM Проверяем наличие docker-compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ docker-compose не установлен. Установите docker-compose и попробуйте снова.
    pause
    exit /b 1
)

REM Создаем необходимые директории
echo 📁 Создание директорий...
if not exist config mkdir config
if not exist logs mkdir logs
if not exist nginx\ssl mkdir nginx\ssl

REM Создаем самоподписанный SSL сертификат для разработки
if not exist nginx\ssl\cert.pem (
    echo 🔐 Создание SSL сертификата для разработки...
    openssl req -x509 -newkey rsa:4096 -keyout nginx\ssl\key.pem -out nginx\ssl\cert.pem -days 365 -nodes -subj "/C=RU/ST=Moscow/L=Moscow/O=3proxy Manager/CN=localhost"
)

REM Собираем образ
echo 🔨 Сборка Docker образа...
docker build -t auth-proxy-manager:latest .

if errorlevel 0 (
    echo ✅ Образ успешно собран!
    echo 🚀 Для запуска используйте: docker-compose up -d
) else (
    echo ❌ Ошибка при сборке образа
    pause
    exit /b 1
)

pause
