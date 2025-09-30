#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример клиента для работы с WebSocket API прокси-сервера
"""

import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("Установите библиотеку websockets: pip install websockets")
    sys.exit(1)


class ProxyWebSocketClient:
    """Клиент для работы с WebSocket API прокси-сервера"""
    
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.websocket = None
        self.is_authenticated = False
    
    async def connect(self):
        """Подключение к WebSocket серверу"""
        print(f"Подключение к {self.url}...")
        self.websocket = await websockets.connect(self.url)
        print("✓ Подключено")
    
    async def send_message(self, message):
        """Отправка сообщения на сервер"""
        if not self.websocket:
            raise Exception("WebSocket не подключен")
        
        message_str = json.dumps(message, ensure_ascii=False)
        print(f"\n→ Отправка: {message_str}")
        await self.websocket.send(message_str)
    
    async def receive_message(self):
        """Получение сообщения от сервера"""
        if not self.websocket:
            raise Exception("WebSocket не подключен")
        
        response = await self.websocket.recv()
        data = json.loads(response)
        print(f"← Получено: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data
    
    async def authenticate(self):
        """Авторизация на сервере"""
        print("\n=== Авторизация ===")
        await self.send_message({
            'type': 'auth',
            'username': self.username,
            'password': self.password
        })
        
        response = await self.receive_message()
        
        if response.get('type') == 'auth_response' and response.get('success'):
            self.is_authenticated = True
            print(f"✓ Успешная авторизация как {response.get('user')}")
            return True
        else:
            print(f"✗ Ошибка авторизации: {response.get('message')}")
            return False
    
    async def get_current_ip(self):
        """Получение текущего IP адреса"""
        if not self.is_authenticated:
            raise Exception("Требуется авторизация")
        
        print("\n=== Получение текущего IP ===")
        await self.send_message({'type': 'get_current_ip'})
        
        response = await self.receive_message()
        
        if response.get('type') == 'current_ip_response' and response.get('success'):
            ip = response.get('ip')
            print(f"✓ Текущий IP: {ip}")
            return ip
        else:
            print(f"✗ Ошибка получения IP")
            return None
    
    async def add_ip(self, ip):
        """Добавление IP в разрешенные"""
        if not self.is_authenticated:
            raise Exception("Требуется авторизация")
        
        print(f"\n=== Добавление IP {ip} ===")
        await self.send_message({
            'type': 'add_ip',
            'ip': ip
        })
        
        response = await self.receive_message()
        
        if response.get('type') == 'add_ip_response':
            if response.get('success'):
                print(f"✓ {response.get('message')}")
                return True
            else:
                print(f"✗ {response.get('message')}")
                return False
        return False
    
    async def get_allowed_ips(self):
        """Получение списка разрешенных IP"""
        if not self.is_authenticated:
            raise Exception("Требуется авторизация")
        
        print("\n=== Получение списка разрешенных IP ===")
        await self.send_message({'type': 'get_allowed_ips'})
        
        response = await self.receive_message()
        
        if response.get('type') == 'allowed_ips_response' and response.get('success'):
            ips = response.get('ips', [])
            print(f"✓ Разрешенные IP адреса ({len(ips)}):")
            for ip in ips:
                print(f"  - {ip}")
            return ips
        else:
            print(f"✗ Ошибка получения списка IP")
            return []
    
    async def restart_proxy(self):
        """Перезапуск прокси сервера"""
        if not self.is_authenticated:
            raise Exception("Требуется авторизация")
        
        print("\n=== Перезапуск прокси сервера ===")
        await self.send_message({'type': 'restart_proxy'})
        
        response = await self.receive_message()
        
        if response.get('type') == 'restart_proxy_response':
            if response.get('success'):
                print(f"✓ {response.get('message')}")
                return True
            else:
                print(f"✗ {response.get('message')}")
                return False
        return False
    
    async def close(self):
        """Закрытие WebSocket соединения"""
        if self.websocket:
            await self.websocket.close()
            print("\n✓ Соединение закрыто")


async def main():
    """Основная функция для демонстрации работы клиента"""
    
    # Параметры подключения
    WS_URL = "ws://localhost:5000/ws"
    USERNAME = "admin"
    PASSWORD = "admin123"
    
    client = ProxyWebSocketClient(WS_URL, USERNAME, PASSWORD)
    
    try:
        # Подключение
        await client.connect()
        
        # Авторизация
        if not await client.authenticate():
            return
        
        # Получение текущего IP
        current_ip = await client.get_current_ip()
        
        # Добавление текущего IP в разрешенные
        if current_ip:
            await client.add_ip(current_ip)
        
        # Получение списка разрешенных IP
        await client.get_allowed_ips()
        
        # Демонстрация добавления пользовательского IP
        print("\n=== Добавление пользовательского IP ===")
        custom_ip = input("Введите IP адрес для добавления (или Enter для пропуска): ").strip()
        if custom_ip:
            await client.add_ip(custom_ip)
            await client.get_allowed_ips()
        
        # Перезапуск прокси (опционально)
        restart = input("\nПерезапустить прокси сервер? (y/N): ").strip().lower()
        if restart == 'y':
            await client.restart_proxy()
        
    except websockets.exceptions.ConnectionClosed:
        print("\n✗ Соединение закрыто сервером")
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
    finally:
        await client.close()


if __name__ == '__main__':
    print("=" * 60)
    print("WebSocket клиент для управления прокси-сервером")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✗ Прервано пользователем")
    
    print("\n" + "=" * 60)
    print("Работа завершена")
    print("=" * 60)

