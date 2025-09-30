# WebSocket API Documentation

## Описание

WebSocket API предоставляет возможность работы с прокси-сервером в режиме реального времени через WebSocket соединение. API поддерживает авторизацию и управление IP-адресами.

## Подключение

```
ws://localhost:5000/ws
```

Для производственного окружения с SSL:
```
wss://your-domain.com/ws
```

## Формат сообщений

Все сообщения передаются в формате JSON.

### Структура запроса
```json
{
    "type": "тип_операции",
    "параметр1": "значение1",
    "параметр2": "значение2"
}
```

### Структура ответа
```json
{
    "type": "тип_ответа",
    "success": true/false,
    "message": "сообщение",
    "данные": "значения"
}
```

## Операции

### 1. Авторизация (auth)

**Запрос:**
```json
{
    "type": "auth",
    "username": "admin",
    "password": "admin123"
}
```

**Ответ (успешный):**
```json
{
    "type": "auth_response",
    "success": true,
    "message": "Авторизация успешна",
    "user": "admin"
}
```

**Ответ (ошибка):**
```json
{
    "type": "auth_response",
    "success": false,
    "message": "Неверные учетные данные"
}
```

### 2. Получение текущего IP (get_current_ip)

**Запрос:**
```json
{
    "type": "get_current_ip"
}
```

**Ответ:**
```json
{
    "type": "current_ip_response",
    "success": true,
    "ip": "123.45.67.89"
}
```

### 3. Добавление IP в разрешенные (add_ip)

**Запрос:**
```json
{
    "type": "add_ip",
    "ip": "123.45.67.89"
}
```

**Ответ (успешный):**
```json
{
    "type": "add_ip_response",
    "success": true,
    "message": "IP 123.45.67.89 добавлен в разрешенные"
}
```

**Ответ (ошибка):**
```json
{
    "type": "add_ip_response",
    "success": false,
    "message": "IP 123.45.67.89 уже в списке или неверный формат"
}
```

### 4. Получение списка разрешенных IP (get_allowed_ips)

**Запрос:**
```json
{
    "type": "get_allowed_ips"
}
```

**Ответ:**
```json
{
    "type": "allowed_ips_response",
    "success": true,
    "ips": ["123.45.67.89", "98.76.54.32"]
}
```

### 5. Перезапуск прокси-сервера (restart_proxy)

**Запрос:**
```json
{
    "type": "restart_proxy"
}
```

**Ответ (успешный):**
```json
{
    "type": "restart_proxy_response",
    "success": true,
    "message": "Прокси сервер перезапущен"
}
```

**Ответ (ошибка):**
```json
{
    "type": "restart_proxy_response",
    "success": false,
    "message": "Ошибка при перезапуске прокси сервера"
}
```

## Обработка ошибок

Если запрос выполнен без авторизации или с ошибкой, сервер вернет сообщение с типом `error`:

```json
{
    "type": "error",
    "message": "Требуется авторизация"
}
```

```json
{
    "type": "error",
    "message": "Неверный формат JSON"
}
```

```json
{
    "type": "error",
    "message": "Неизвестный тип сообщения: unknown_type"
}
```

## Примеры использования

### JavaScript (Browser)

```javascript
// Подключение
const ws = new WebSocket('ws://localhost:5000/ws');

ws.onopen = () => {
    console.log('Подключено');
    
    // Авторизация
    ws.send(JSON.stringify({
        type: 'auth',
        username: 'admin',
        password: 'admin123'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Получено:', data);
    
    if (data.type === 'auth_response' && data.success) {
        // Авторизация успешна, получаем текущий IP
        ws.send(JSON.stringify({
            type: 'get_current_ip'
        }));
    }
    
    if (data.type === 'current_ip_response') {
        // Добавляем текущий IP в разрешенные
        ws.send(JSON.stringify({
            type: 'add_ip',
            ip: data.ip
        }));
    }
};

ws.onerror = (error) => {
    console.error('WebSocket ошибка:', error);
};

ws.onclose = () => {
    console.log('Соединение закрыто');
};
```

### Python (websockets)

```python
import asyncio
import websockets
import json

async def proxy_client():
    uri = "ws://localhost:5000/ws"
    
    async with websockets.connect(uri) as websocket:
        # Авторизация
        await websocket.send(json.dumps({
            'type': 'auth',
            'username': 'admin',
            'password': 'admin123'
        }))
        
        response = await websocket.recv()
        auth_data = json.loads(response)
        print(f"Авторизация: {auth_data}")
        
        if auth_data.get('success'):
            # Получение текущего IP
            await websocket.send(json.dumps({
                'type': 'get_current_ip'
            }))
            
            response = await websocket.recv()
            ip_data = json.loads(response)
            print(f"Текущий IP: {ip_data}")
            
            # Добавление IP в разрешенные
            await websocket.send(json.dumps({
                'type': 'add_ip',
                'ip': ip_data.get('ip')
            }))
            
            response = await websocket.recv()
            add_data = json.loads(response)
            print(f"Добавление IP: {add_data}")

asyncio.run(proxy_client())
```

## Тестирование

Для тестирования WebSocket API используйте прилагаемый HTML-клиент `ws_client.html`:

1. Откройте файл `ws_client.html` в браузере
2. Нажмите "Подключиться"
3. Введите учетные данные (по умолчанию: admin/admin123)
4. Нажмите "Авторизоваться"
5. Используйте доступные операции для управления IP-адресами

## Безопасность

1. **Авторизация обязательна**: Все операции (кроме авторизации) требуют предварительной авторизации через WebSocket
2. **Валидация IP**: Все IP-адреса валидируются перед добавлением
3. **Сессионная авторизация**: Авторизация действует только в рамках одного WebSocket соединения
4. **SSL/TLS**: В продакшене используйте WSS (WebSocket Secure) через HTTPS/SSL

## Параллельная работа HTTP и WebSocket API

WebSocket API работает параллельно с существующим HTTP API. Вы можете использовать оба API одновременно:

- **HTTP API**: Для простых запросов и интеграции с существующими системами
- **WebSocket API**: Для приложений реального времени, длительных соединений и двусторонней коммуникации

## Ограничения

- Одно WebSocket соединение = одна сессия авторизации
- При разрыве соединения необходимо авторизоваться заново
- Перезапуск прокси требует sudo прав на сервере

## Поддержка

Для вопросов и предложений создавайте issue в репозитории проекта.

