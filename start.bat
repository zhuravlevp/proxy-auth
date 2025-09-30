@echo off
echo ========================================
echo   3proxy Management Service
echo ========================================
echo.
echo Установка зависимостей...
pip install -r requirements.txt
echo.
echo Запуск сервера...
echo Веб-интерфейс: http://localhost:5000
echo Клиент: откройте client.html в браузере
echo.
echo Логин: admin
echo Пароль: admin123
echo.
echo Нажмите Ctrl+C для остановки
echo ========================================
python run.py
pause
