#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки миграции на aiohttp
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Тестирует импорты основных модулей"""
    try:
        print("🔍 Тестирование импортов...")
        
        # Тестируем основные импорты
        import aiohttp
        print("✅ aiohttp импортирован")
        
        import aiofiles
        print("✅ aiofiles импортирован")
        
        import bcrypt
        print("✅ bcrypt импортирован")
        
        from aiohttp_session import setup, get_session, new_session
        print("✅ aiohttp_session импортирован")
        
        from aiohttp_cors import setup as cors_setup
        print("✅ aiohttp_cors импортирован")
        
        from aiohttp_jinja2 import setup as jinja_setup, render_template
        print("✅ aiohttp_jinja2 импортирован")
        
        # Тестируем импорт нашего приложения
        from app import create_app, proxy_manager
        print("✅ app.py импортирован")
        
        print("🎉 Все импорты успешны!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

async def test_proxy_manager():
    """Тестирует ProxyManager"""
    try:
        print("\n🔍 Тестирование ProxyManager...")
        
        from app import proxy_manager
        
        # Тестируем получение разрешенных IP
        allowed_ips = await proxy_manager.get_allowed_ips()
        print(f"✅ Получен список IP: {len(allowed_ips)} записей")
        
        # Тестируем получение текущего IP
        current_ip = await proxy_manager.get_current_ip()
        print(f"✅ Текущий IP: {current_ip}")
        
        print("🎉 ProxyManager работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка ProxyManager: {e}")
        return False

async def test_app_creation():
    """Тестирует создание приложения"""
    try:
        print("\n🔍 Тестирование создания приложения...")
        
        from app import create_app
        app = create_app()
        
        print(f"✅ Приложение создано: {type(app)}")
        print(f"✅ Количество маршрутов: {len(app.router.routes())}")
        
        print("🎉 Приложение создается корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания приложения: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование миграции на aiohttp")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_proxy_manager,
        test_app_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Миграция успешна!")
        return True
    else:
        print("❌ Некоторые тесты не пройдены. Проверьте зависимости.")
        return False

if __name__ == '__main__':
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Тестирование прервано")
        sys.exit(1)
