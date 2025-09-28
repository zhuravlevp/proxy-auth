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
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Включаем CORS для работы с Chrome расширением
CORS(app, supports_credentials=True)

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
    
    def get_current_ip(self):
        """Получает текущий внешний IP адрес"""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
        except:
            try:
                response = requests.get('https://ipinfo.io/ip', timeout=5)
                return response.text.strip()
            except:
                return "Не удалось определить IP"
    
    def add_allowed_ip(self, ip):
        """Добавляет IP в список разрешенных"""
        try:
            # Валидация IP
            ipaddress.ip_address(ip)
            
            # Читаем текущий список
            allowed_ips = self.get_allowed_ips()
            
            if ip not in allowed_ips:
                allowed_ips.append(ip)
                
                # Записываем обновленный список
                with open(self.allowed_ips_file, 'w') as f:
                    f.write("# Разрешенные IP адреса\n")
                    for allowed_ip in allowed_ips:
                        f.write(f"{allowed_ip}\n")
                
                # Обновляем конфиг 3proxy
                self.update_proxy_config(allowed_ips)
                return True
            return False
        except ValueError:
            return False
    
    def get_allowed_ips(self):
        """Получает список разрешенных IP"""
        allowed_ips = []
        if os.path.exists(self.allowed_ips_file):
            with open(self.allowed_ips_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        allowed_ips.append(line)
        return allowed_ips
    
    def update_proxy_config(self, allowed_ips):
        """Обновляет конфигурацию 3proxy с новыми разрешенными IP"""
        config_lines = []
        
        # Читаем существующий конфиг
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config_lines = f.readlines()
        
        # Удаляем старые allow правила
        config_lines = [line for line in config_lines if not line.strip().startswith('allow')]
        
        # Добавляем новые allow правила
        for ip in allowed_ips:
            config_lines.append(f"allow {ip}\n")
        
        # Записываем обновленный конфиг
        with open(self.config_file, 'w') as f:
            f.writelines(config_lines)
    
    def restart_proxy(self):
        """Перезапускает 3proxy (требует sudo)"""
        try:
            # Останавливаем 3proxy
            subprocess.run(['sudo', 'pkill', '3proxy'], check=False)
            # Запускаем 3proxy с новой конфигурацией
            subprocess.run(['sudo', '3proxy', self.config_file], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

# Инициализируем менеджер прокси
proxy_manager = ProxyManager()

# Простая система пользователей (в продакшене используйте базу данных)
users = {
    'admin': generate_password_hash('admin123')
}

def login_required(f):
    """Декоратор для проверки авторизации"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
@login_required
def index():
    """Главная страница"""
    current_ip = proxy_manager.get_current_ip()
    allowed_ips = proxy_manager.get_allowed_ips()
    return render_template('index.html', 
                         current_ip=current_ip, 
                         allowed_ips=allowed_ips)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница авторизации"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and check_password_hash(users[username], password):
            session['user_id'] = username
            flash('Успешная авторизация!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверные учетные данные!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Выход из системы"""
    session.pop('user_id', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/allow_ip', methods=['POST'])
@login_required
def allow_ip():
    """API для добавления IP в разрешенные"""
    data = request.get_json()
    ip = data.get('ip')
    
    if not ip:
        return jsonify({'success': False, 'message': 'IP адрес не указан'})
    
    if proxy_manager.add_allowed_ip(ip):
        return jsonify({'success': True, 'message': f'IP {ip} добавлен в разрешенные'})
    else:
        return jsonify({'success': False, 'message': f'IP {ip} уже в списке или неверный формат'})

@app.route('/api/current_ip')
@login_required
def api_current_ip():
    """API для получения текущего IP"""
    current_ip = proxy_manager.get_current_ip()
    return jsonify({'ip': current_ip})

@app.route('/api/allowed_ips')
@login_required
def api_allowed_ips():
    """API для получения списка разрешенных IP"""
    allowed_ips = proxy_manager.get_allowed_ips()
    return jsonify({'ips': allowed_ips})

@app.route('/restart_proxy', methods=['POST'])
@login_required
def restart_proxy():
    """Перезапуск прокси сервера"""
    if proxy_manager.restart_proxy():
        return jsonify({'success': True, 'message': 'Прокси сервер перезапущен'})
    else:
        return jsonify({'success': False, 'message': 'Ошибка при перезапуске прокси сервера'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
