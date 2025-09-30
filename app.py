#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3proxy Configuration Management Service
Сервис для управления конфигурацией 3proxy
"""

import os
import json
import subprocess
import ipaddress
import asyncio
import aiofiles
from datetime import datetime
from aiohttp import web, ClientSession, ClientTimeout, WSMsgType
from aiohttp_session import setup, get_session, new_session, SimpleCookieStorage
from aiohttp_cors import setup as cors_setup, ResourceOptions
from aiohttp_jinja2 import setup as jinja_setup, render_template
import jinja2
import bcrypt
import aiohttp

# Конфигурация
CONFIG_FILE = '3proxy.cfg'
ALLOWED_IPS_FILE = 'allowed_ips.txt'

class ProxyManager:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.allowed_ips_file = ALLOWED_IPS_FILE
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """Создает необходимые файлы если их нет"""
        if not os.path.exists(self.config_file):
            self.create_default_config()
        
        if not os.path.exists(self.allowed_ips_file):
            with open(self.allowed_ips_file, 'w') as f:
                f.write("# Разрешенные IP адреса\n")
    
    def create_default_config(self):
        """Создает базовую конфигурацию 3proxy"""
        default_config = """# 3proxy configuration
daemon
maxconn 100
nserver 8.8.8.8
nserver 8.8.4.4

# Authentication
auth strong

# Users
users admin:CL:admin123

# Access control
allow admin

# Proxy settings
proxy -p3128 -a
"""
        with open(self.config_file, 'w') as f:
            f.write(default_config)
    
    async def get_current_ip(self):
        """Получает текущий внешний IP адрес"""
        timeout = ClientTimeout(total=5)
        try:
            async with ClientSession(timeout=timeout) as session:
                async with session.get('https://api.ipify.org') as response:
                    if response.status == 200:
                        return (await response.text()).strip()
        except:
            try:
                async with ClientSession(timeout=timeout) as session:
                    async with session.get('https://ipinfo.io/ip') as response:
                        if response.status == 200:
                            return (await response.text()).strip()
            except:
                pass
        return "Не удалось определить IP"
    
    async def add_allowed_ip(self, ip):
        """Добавляет IP в список разрешенных"""
        try:
            # Валидация IP
            ipaddress.ip_address(ip)
            
            # Читаем текущий список
            allowed_ips = await self.get_allowed_ips()
            
            if ip not in allowed_ips:
                allowed_ips.append(ip)
                
                # Записываем обновленный список
                content = "# Разрешенные IP адреса\n" + "\n".join(allowed_ips) + "\n"
                async with aiofiles.open(self.allowed_ips_file, 'w') as f:
                    await f.write(content)
                
                # Обновляем конфиг 3proxy
                await self.update_proxy_config(allowed_ips)
                return True
            return False
        except ValueError:
            return False
    
    async def get_allowed_ips(self):
        """Получает список разрешенных IP"""
        allowed_ips = []
        if os.path.exists(self.allowed_ips_file):
            async with aiofiles.open(self.allowed_ips_file, 'r') as f:
                content = await f.read()
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        allowed_ips.append(line)
        return allowed_ips
    
    async def update_proxy_config(self, allowed_ips):
        """Обновляет конфигурацию 3proxy с новыми разрешенными IP"""
        config_lines = []
        
        # Читаем существующий конфиг
        if os.path.exists(self.config_file):
            async with aiofiles.open(self.config_file, 'r') as f:
                content = await f.read()
                config_lines = content.splitlines()
        
        # Удаляем старые allow правила
        config_lines = [line for line in config_lines if not line.strip().startswith('allow')]
        
        # Добавляем новые allow правила
        for ip in allowed_ips:
            config_lines.append(f"allow {ip}")
        
        # Записываем обновленный конфиг
        content = "\n".join(config_lines) + "\n"
        async with aiofiles.open(self.config_file, 'w') as f:
            await f.write(content)
    
    async def restart_proxy(self):
        """Перезапускает 3proxy (требует sudo)"""
        try:
            # Останавливаем 3proxy
            process = await asyncio.create_subprocess_exec(
                'sudo', 'pkill', '3proxy',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            # Запускаем 3proxy с новой конфигурацией
            process = await asyncio.create_subprocess_exec(
                'sudo', '3proxy', self.config_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return True
        except Exception:
            return False

# Инициализируем менеджер прокси
proxy_manager = ProxyManager()

# Простая система пользователей (в продакшене используйте базу данных)
users = {
    'admin': bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
}

def login_required(f):
    """Декоратор для проверки авторизации"""
    async def decorated_function(request):
        session = await get_session(request)
        if 'user_id' not in session:
            return web.HTTPFound('/login')
        return await f(request)
    return decorated_function

async def index(request):
    """Главная страница"""
    session = await get_session(request)
    current_ip = await proxy_manager.get_current_ip()
    allowed_ips = await proxy_manager.get_allowed_ips()
    return render_template('index.html', request, {
        'current_ip': current_ip,
        'allowed_ips': allowed_ips,
        'session': session
    })

async def login(request):
    """Страница авторизации"""
    session = await get_session(request)
    
    if request.method == 'POST':
        data = await request.post()
        username = data.get('username')
        password = data.get('password')
        
        if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username]):
            session = await new_session(request)
            session['user_id'] = username
            return web.HTTPFound('/')
        else:
            session = await get_session(request)
            return render_template('login.html', request, {
                'error': 'Неверные учетные данные!',
                'session': session
            })
    
    return render_template('login.html', request, {'session': session})

async def logout(request):
    """Выход из системы"""
    session = await get_session(request)
    session.invalidate()
    return web.HTTPFound('/login')

async def allow_ip(request):
    """API для добавления IP в разрешенные"""
    data = await request.json()
    ip = data.get('ip')
    
    if not ip:
        return web.json_response({'success': False, 'message': 'IP адрес не указан'})
    
    if await proxy_manager.add_allowed_ip(ip):
        return web.json_response({'success': True, 'message': f'IP {ip} добавлен в разрешенные'})
    else:
        return web.json_response({'success': False, 'message': f'IP {ip} уже в списке или неверный формат'})

async def api_current_ip(request):
    """API для получения текущего IP"""
    current_ip = await proxy_manager.get_current_ip()
    return web.json_response({'ip': current_ip})

async def api_allowed_ips(request):
    """API для получения списка разрешенных IP"""
    allowed_ips = await proxy_manager.get_allowed_ips()
    return web.json_response({'ips': allowed_ips})

async def restart_proxy(request):
    """Перезапуск прокси сервера"""
    if await proxy_manager.restart_proxy():
        return web.json_response({'success': True, 'message': 'Прокси сервер перезапущен'})
    else:
        return web.json_response({'success': False, 'message': 'Ошибка при перезапуске прокси сервера'})

async def websocket_handler(request):
    """WebSocket обработчик для авторизации и управления IP"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    # Флаг авторизации для текущего WebSocket соединения
    is_authenticated = False
    authenticated_user = None
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    msg_type = data.get('type')
                    
                    # Обработка авторизации
                    if msg_type == 'auth':
                        username = data.get('username')
                        password = data.get('password')
                        
                        if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username]):
                            is_authenticated = True
                            authenticated_user = username
                            await ws.send_json({
                                'type': 'auth_response',
                                'success': True,
                                'message': 'Авторизация успешна',
                                'user': username
                            })
                        else:
                            await ws.send_json({
                                'type': 'auth_response',
                                'success': False,
                                'message': 'Неверные учетные данные'
                            })
                    
                    # Получение текущего IP
                    elif msg_type == 'get_current_ip':
                        if not is_authenticated:
                            await ws.send_json({
                                'type': 'error',
                                'message': 'Требуется авторизация'
                            })
                            continue
                        
                        current_ip = await proxy_manager.get_current_ip()
                        await ws.send_json({
                            'type': 'current_ip_response',
                            'success': True,
                            'ip': current_ip
                        })
                    
                    # Добавление IP в разрешенные
                    elif msg_type == 'add_ip':
                        if not is_authenticated:
                            await ws.send_json({
                                'type': 'error',
                                'message': 'Требуется авторизация'
                            })
                            continue
                        
                        ip = data.get('ip')
                        if not ip:
                            await ws.send_json({
                                'type': 'add_ip_response',
                                'success': False,
                                'message': 'IP адрес не указан'
                            })
                            continue
                        
                        if await proxy_manager.add_allowed_ip(ip):
                            await ws.send_json({
                                'type': 'add_ip_response',
                                'success': True,
                                'message': f'IP {ip} добавлен в разрешенные'
                            })
                        else:
                            await ws.send_json({
                                'type': 'add_ip_response',
                                'success': False,
                                'message': f'IP {ip} уже в списке или неверный формат'
                            })
                    
                    # Получение списка разрешенных IP
                    elif msg_type == 'get_allowed_ips':
                        if not is_authenticated:
                            await ws.send_json({
                                'type': 'error',
                                'message': 'Требуется авторизация'
                            })
                            continue
                        
                        allowed_ips = await proxy_manager.get_allowed_ips()
                        await ws.send_json({
                            'type': 'allowed_ips_response',
                            'success': True,
                            'ips': allowed_ips
                        })
                    
                    # Перезапуск прокси
                    elif msg_type == 'restart_proxy':
                        if not is_authenticated:
                            await ws.send_json({
                                'type': 'error',
                                'message': 'Требуется авторизация'
                            })
                            continue
                        
                        if await proxy_manager.restart_proxy():
                            await ws.send_json({
                                'type': 'restart_proxy_response',
                                'success': True,
                                'message': 'Прокси сервер перезапущен'
                            })
                        else:
                            await ws.send_json({
                                'type': 'restart_proxy_response',
                                'success': False,
                                'message': 'Ошибка при перезапуске прокси сервера'
                            })
                    
                    else:
                        await ws.send_json({
                            'type': 'error',
                            'message': f'Неизвестный тип сообщения: {msg_type}'
                        })
                
                except json.JSONDecodeError:
                    await ws.send_json({
                        'type': 'error',
                        'message': 'Неверный формат JSON'
                    })
                except Exception as e:
                    await ws.send_json({
                        'type': 'error',
                        'message': f'Ошибка обработки запроса: {str(e)}'
                    })
            
            elif msg.type == WSMsgType.ERROR:
                print(f'WebSocket соединение закрыто с ошибкой: {ws.exception()}')
    
    finally:
        print(f'WebSocket соединение закрыто для пользователя: {authenticated_user or "неавторизованный"}')
    
    return ws

def create_app():
    """Создает и настраивает приложение"""
    app = web.Application()
    
    # Настройка сессий
    # Используем SimpleCookieStorage (без шифрования)
    # Для продакшена рекомендуется использовать Redis или другое хранилище сессий с шифрованием
    setup(app, SimpleCookieStorage())
    
    # Настройка CORS
    cors = cors_setup(app, defaults={
        "*": ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Настройка шаблонов
    import os
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    jinja_setup(app, loader=jinja2.FileSystemLoader(template_path))
    
    # Маршруты
    app.router.add_get('/', login_required(index))
    app.router.add_get('/login', login)
    app.router.add_post('/login', login)
    app.router.add_get('/logout', logout)
    app.router.add_post('/allow_ip', login_required(allow_ip))
    app.router.add_get('/api/current_ip', login_required(api_current_ip))
    app.router.add_get('/api/allowed_ips', login_required(api_allowed_ips))
    app.router.add_post('/restart_proxy', login_required(restart_proxy))
    
    # WebSocket маршрут
    app.router.add_get('/ws', websocket_handler)
    
    # Настройка CORS для всех маршрутов (кроме статических)
    for route in list(app.router.routes()):
        if not isinstance(route.resource, web.StaticResource):
            try:
                cors.add(route)
            except ValueError:
                # Пропускаем маршруты, которые уже имеют CORS
                pass
    
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=5000)
