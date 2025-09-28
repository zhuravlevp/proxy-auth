#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт запуска сервиса управления 3proxy
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("🚀 Запуск сервиса управления 3proxy...")
    print("📱 Веб-интерфейс: http://localhost:5000")
    print("🔑 Логин: admin, Пароль: admin123")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Сервис остановлен")
        sys.exit(0)
