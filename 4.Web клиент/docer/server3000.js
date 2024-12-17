const http = require('http');
const Redis = require('ioredis');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// Создаем экземпляр Redis
const redis = new Redis(); // По умолчанию подключается к localhost:6379

// Функция для получения значения куки по имени
function getCookie(req, name) {
    const cookies = req.headers.cookie;
    if (!cookies) return null;

    const cookieArr = cookies.split('; ');
    for (let cookie of cookieArr) {
        const [key, value] = cookie.split('=');
        if (key === name) {
            return value;
        }
    }
    return null;
}

// Функция для генерации токена
function generateToken() {
    return crypto.randomBytes(16).toString('hex');
}

// Функция для выполнения запроса к Redis
async function requestToRedis(sessionToken) {
    try {
        const data = await redis.get(sessionToken);
        if (data) {
            return { success: true, data: JSON.parse(data) };
        } else {
            return { success: false, message: 'Session token not found in Redis' };
        }
    } catch (error) {
        console.error('Error fetching data from Redis:', error);
        return { success: false, message: error.message };
    }
}

// Создаем сервер
const server = http.createServer(async (req, res) => {
    const sessionToken = getCookie(req, 'session_token');

    // Обработка URL
    if (req.url === '/') {
        // Генерируем новый токен для state
        const loginToken = generateToken();

        // Страница авторизации
        res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
        
        // Чтение HTML-файла
        fs.readFile(path.join(__dirname, 'authPage.html'), 'utf8', (err, data) => {
            if (err) {
                res.writeHead(500, { 'Content-Type': 'text/plain;charset=utf-8' });
                res.end('Ошибка сервера\n');
                return;
            }

            // Заменяем loginToken в HTML-коде
            const responseHtml = data
                .replace(/loginToken/g, loginToken); // Заменяем все вхождения loginToken на новый токен

            res.end(responseHtml);
        });
    } else if (req.url.startsWith('/login')) {
        const urlParams = new URLSearchParams(req.url.split('?')[1]);
        const type = urlParams.get('type');
        const state = urlParams.get('state');

        if (!type || !state) {
            // Редирект на главную
            res.writeHead(302, { Location: '/' });
            res.end();
            return;
        }

        // Генерируем новый токен сессии и токен входа
        const newSessionToken = generateToken();
        const loginToken = generateToken();

        // Сохраняем токен сессии в Redis
        const userData = {
            status: 'Анонимный',
            loginToken: loginToken
        };
        await redis.set(newSessionToken, JSON.stringify(userData));

        // Здесь должна быть логика для модуля авторизации
        // Например, отправка запроса на авторизацию с использованием loginToken
        // Для примера просто отправим ответ
        res.setHeader('Set-Cookie', `session_token=${newSessionToken}; HttpOnly`);
        res.writeHead(200, { 'Content-Type': 'text/plain;charset=utf-8' });
        res.end(`Вы успешно авторизованы через ${type}. Ваш токен входа: ${loginToken}`);
    } else {
        // Если URL не распознан, возвращаем 404
        res.writeHead(404, { 'Content-Type': 'text/plain;charset=utf-8' });
        res.end('404 Not Found\n');
    }
});

// Запускаем сервер на порту 3000
const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Сервер запущен на http://localhost:${PORT}/`);
});