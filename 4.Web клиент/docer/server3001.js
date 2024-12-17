const http = require('http');
const Redis = require('ioredis');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const axios = require('axios'); // Добавляем axios для выполнения HTTP-запросов

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

// Создаем сервер
const server = http.createServer(async (req, res) => {
    const sessionToken = getCookie(req, 'session_token');

    // Проверяем наличие токена сессии
    if (!sessionToken) {
        // Если токена нет, сразу считаем ответ от Redis отрицательным
        res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
        res.end('<h1>Пожалуйста, авторизуйтесь через: GitHub, Яндекс ID или через код.</h1>');
        return;
    }

    // Обработка URL
    if (req.url === '/') {
        // Страница авторизации
        res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
        fs.readFile(path.join(__dirname, 'authPage.html'), 'utf8', (err, data) => {
            if (err) {
                res.writeHead(500, { 'Content-Type': 'text/plain;charset=utf-8' });
                res.end('Ошибка сервера\n');
                return;
            }
            res.end(data);
        });
    } else if (req.url.startsWith('/login')) {
        const urlParams = new URLSearchParams(req.url.split('?')[1]);
        const type = urlParams.get('type');

        if (!type) {
            // Редирект на главную, если параметров нет
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

        // Формируем URL для модуля авторизации
        const authUrl = `http://193.164.17.124:8080/oauth?type=${type}&state=${loginToken}`;

        try {
            // Делаем запрос к модулю авторизации
            const response = await axios.get(authUrl);
            // Обработка ответа от модуля авторизации
            if (response.status === 200) {
                console.log('Ответ от модуля авторизации:', response.data);
            
                // Проверяем, есть ли URL в ответе
                if (response.data.URL) {
                    // Если есть URL, создаем кнопку для перехода
                    res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
                    res.end(`
                        <h1>Пожалуйста, перейдите по следующей ссылке для авторизации:</h1>
                        <a href="${response.data.URL}" target="_blank">
                            <button>Авторизоваться</button>
                        </a>
                    `);
                } else if (response.data.code) {
                    // Если есть code, выводим его пользователю
                    res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
                    res.end(`
                        <h1>Ваш код авторизации:</h1>
                        <p>${response.data.code}</p>
                    `);
                } else {
                    // Если ни URL, ни code нет, обрабатываем как ошибку
                    res.writeHead(400, { 'Content-Type': 'text/plain;charset=utf-8' });
                    res.end('Ошибка авторизации: не получен URL или код\n');
                }
            } else {
                // Обработка ошибок авторизации
                res.writeHead(400, { 'Content-Type': 'text/plain;charset=utf-8' });
                res.end('Ошибка авторизации\n');
            }
        } catch (error) {
            console.error('Ошибка при запросе к модулю авторизации:', error);
            res.writeHead(500, { 'Content-Type': 'text/plain;charset=utf-8' });
            res.end('Ошибка сервера при авторизации\n');
        }
    } else {
        // Если URL не распознан, возвращаем 404
        res.writeHead(404, { 'Content-Type': 'text/plain;charset=utf-8' });
        res.end('404 Not Found\n');
    }
});

// Запускаем сервер на порту 3001
const PORT = 3001;
server.listen(PORT, () => {
    console.log(`Сервер запущен на http://localhost:${PORT}/`);
});