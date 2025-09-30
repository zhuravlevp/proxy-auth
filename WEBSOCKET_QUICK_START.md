# WebSocket API - Быстрый старт

## Запуск сервера

Сервер уже настроен и готов к работе. WebSocket API доступен на эндпоинте `/ws`.

```bash
# Запуск сервера
cd proxy-auth
python app.py
```

Сервер запустится на `http://localhost:5000`, WebSocket будет доступен на `ws://localhost:5000/ws`.

## Тестирование с HTML клиентом

1. Запустите сервер (см. выше)
2. Откройте в браузере файл `ws_client.html`
3. Нажмите "Подключиться"
4. Введите учетные данные (по умолчанию: admin/admin123)
5. Нажмите "Авторизоваться"
6. Теперь доступны все операции с IP адресами

## Тестирование с Python клиентом

1. Установите зависимости:
```bash
pip install websockets
```

2. Запустите пример:
```bash
python ws_client_example.py
```

## Основные операции через WebSocket

### 1. Авторизация
```json
{
    "type": "auth",
    "username": "admin",
    "password": "admin123"
}
```

### 2. Получить текущий IP
```json
{
    "type": "get_current_ip"
}
```

### 3. Добавить IP в разрешенные
```json
{
    "type": "add_ip",
    "ip": "123.45.67.89"
}
```

### 4. Получить список разрешенных IP
```json
{
    "type": "get_allowed_ips"
}
```

### 5. Перезапустить прокси
```json
{
    "type": "restart_proxy"
}
```

## Типичный workflow

1. **Подключение к WebSocket**: `ws://localhost:5000/ws`
2. **Авторизация**: отправить сообщение с типом `auth`
3. **Получить текущий IP**: отправить сообщение с типом `get_current_ip`
4. **Добавить IP в разрешенные**: отправить сообщение с типом `add_ip` с полученным IP
5. **Проверить список**: отправить сообщение с типом `get_allowed_ips`

## Интеграция в ваше приложение

### JavaScript (Browser/Node.js)
```javascript
const ws = new WebSocket('ws://localhost:5000/ws');

ws.onopen = () => {
    // Авторизация
    ws.send(JSON.stringify({
        type: 'auth',
        username: 'admin',
        password: 'admin123'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Обработка ответов
    console.log(data);
};
```

### Python (asyncio + websockets)
```python
import asyncio
import websockets
import json

async def connect():
    async with websockets.connect('ws://localhost:5000/ws') as ws:
        # Авторизация
        await ws.send(json.dumps({
            'type': 'auth',
            'username': 'admin',
            'password': 'admin123'
        }))
        response = await ws.recv()
        print(json.loads(response))

asyncio.run(connect())
```

## Преимущества WebSocket API

1. **Двусторонняя связь**: сервер может отправлять уведомления клиенту
2. **Низкая задержка**: постоянное соединение без overhead HTTP запросов
3. **Эффективность**: одно соединение для множества операций
4. **Real-time**: идеально для приложений реального времени

## Безопасность

⚠️ **Важно**: 
- В продакшене используйте `wss://` (WebSocket Secure)
- Измените пароль по умолчанию
- Используйте HTTPS/SSL для всего приложения
- Настройте правильную аутентификацию

## Troubleshooting

### WebSocket не подключается
- Проверьте, что сервер запущен
- Проверьте URL (должен начинаться с `ws://` или `wss://`)
- Проверьте firewall и network settings

### Ошибка авторизации
- Проверьте username и password
- Убедитесь, что сервер правильно настроен

### Операции не выполняются
- Убедитесь, что вы авторизованы (отправили `auth` и получили `success: true`)
- Проверьте формат JSON сообщений

## Дополнительная информация

Полная документация: см. `WEBSOCKET_API.md`

