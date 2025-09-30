#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт запуска сервиса управления 3proxy
"""

import os
import sys
import asyncio
from aiohttp import web
from app import create_app

async def main():
    print("🚀 Запуск сервиса управления 3proxy...")
    print("📱 Веб-интерфейс: http://localhost:5000")
    print("🔐 Страница входа: http://localhost:5000/login")
    print("🔑 Логин: admin, Пароль: admin123")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()
    
    print("✅ Сервер запущен на http://0.0.0.0:5000")
    print("📋 Доступные маршруты:")
    for route in app.router.routes():
        print(f"   {route.method:6} {route.resource}")
    
    try:
        # Держим сервер запущенным
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Сервис остановлен")
        await runner.cleanup()
        sys.exit(0)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Сервис остановлен")
        sys.exit(0)
