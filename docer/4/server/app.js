const express = require('express');
const cookieParser = require('cookie-parser');
const fs = require('fs');
const path = require('path');
const Redis = require('ioredis');
const axios = require('axios'); 
const crypto = require('crypto');
//const axios = require('axios');

const app = express();
app.use(cookieParser());

const redis = new Redis(); // По умолчанию подключается к localhost:6379
// Сохраняем токен сессии в Redis
async function saveSessionToken(sessionToken,inputToken) {
    const userData = {
        status: 'Анонимный',
        inputToken: inputToken
    };

    try {
        await redis.set(sessionToken, JSON.stringify(userData));
    } catch (error) {
        console.error('Ошибка при сохранении токена сессии в Redis:', error);
    }
}
// Функция для выполнения запроса к Redis
async function requestToRedis(sessionToken) {
    try {
        const data = await redis.get(sessionToken);
        if (data) {
            return { success: true, data: JSON.parse(data),message:"ok"};
        } else {
            return { success: false, message: 'Токен сессии не найден в Redis',data:JSON  };
        }
    } catch (error) {
        console.error('Ошибка при получении данных из Redis:', error);
        return { success: false, message: 'Ошибка при получении данных из Redis: ' + error.message,data:JSON };
    }
}
// Обновляем токен входа в Redis
async function updateSessionToken(sessionToken, newInputToken,status) {
    const userData = {
        status: status,
        inputToken: newInputToken
    };

    try {
        // Сохраняем или обновляем токен сессии в Redis
        await redis.set(sessionToken, JSON.stringify(userData));
        console.log('Токен сессии успешно обновлён');
    } catch (error) {
        console.error('Ошибка при обновлении токена сессии в Redis:', error);
    }
}
// удаляем токен входа в Redis
async function deleteSessionToken(sessionToken) {
    try {
        // Удаляем токен сессии из Redis
        await redis.del(sessionToken);
    } catch (error) {
        console.error('Ошибка при удалении токена сессии из Redis:', error);
    }
}
// Функция для генерации токена
function generateToken() {
    return crypto.randomBytes(16).toString('hex');
}
async function valedTocen(req){

    const sessionToken =req.cookies.session_token
    if(sessionToken==null){
        return false
    }
    logRedis = await requestToRedis(sessionToken);
    
    if(logRedis.success){
        if(logRedis.data.status=='Авторизованный'){
            return true
        }
        else{
            const authUrl = `http://localhost:8080/func/valedtocen?state=${logRedis.data.inputToken}`;
            try {
                const response = await axios.get(authUrl);
                if (response.status === 200) {
                    if(response.data.state=='доступ получен'){
                        deleteSessionToken(sessionToken)
                    const userData = {
                        status: 'Авторизованный',
                        AccessToken: response.data.TokenD,
                        RefreshToken: response.data.TokenU
                    };
                    try {
                        await redis.set(sessionToken, JSON.stringify(userData));
                        console.log(userData);
                        return true
                    } catch (error) {
                        console.error('Ошибка при сохранении токена сессии в Redis:', error);
                        return false
                    }
                    }
                    return false
                }else if(response.status == 401 || response.status == 400){
                    console.log('sessionToken УДАЛЁН');
                    deleteSessionToken(sessionToken);
                    return false
                }
            } catch (error) {
                console.error('мб не опознанный токен');
                return false
            }
        }
    }
    return false;
};

app.use(express.static(path.join(__dirname, '../html')));

app.get('/', async (req, res) => {
    const value = await valedTocen(req);
    if(value){
        res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
        fs.readFile(path.join(__dirname, '../html/profile.html'), 'utf8', (err, data) => {
                if (err) {
                    res.writeHead(500, { 'Content-Type': 'text/plain;charset=utf-8' });
                    res.end('Ошибка сервера\n');
                    return;
                }
                res.end(data);
        });
    }
    else{
        res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
        fs.readFile(path.join(__dirname, '../html/authPage.html'), 'utf8', (err, data) => {
                if (err) {
                    res.writeHead(500, { 'Content-Type': 'text/plain;charset=utf-8' });
                    res.end('Ошибка сервера\n');
                    return;
                }
                res.end(data);
        });
    }
});
app.get('/login', async (req, res) => {
    try {
        const value = await valedTocen(req);
        if (value || Object.keys(req.query).length === 0) {
            return res.redirect('/');
        }

        const type = req.query.type;
        let sessionToken = req.cookies.session_token;
        const logRedis = await requestToRedis(sessionToken);
        const inputToken = generateToken();

        if (!logRedis.success) {
            console.log("новый токен сесии");
            sessionToken = generateToken();
            await saveSessionToken(sessionToken, inputToken);
        } else {
            await updateSessionToken(sessionToken, inputToken, 'Анонимный');
        }

        const authUrl = `http://localhost:8080/oauth?type=${type}&state=${inputToken}`;
        const response = await axios.get(authUrl);

        if (response.status === 200) {
            console.log('Ответ от модуля авторизации:', response.data);
            res.cookie('session_token', sessionToken, { maxAge: 900000, httpOnly: true });

            if (response.data.URL) {
                return res.redirect(response.data.URL);
            } else if (response.data.code) {
                // Читаем HTML-файл и заменяем переменную code
                fs.readFile(path.join(__dirname, '../html/codePage.html'), 'utf8', (err, html) => {
                    if (err) {
                        console.error('Ошибка при чтении HTML-файла:', err);
                        res.writeHead(500, { 'Content-Type': 'text/plain;charset=utf-8' });
                        return res.end('Ошибка сервера при авторизации\n');
                    }
                    // Заменяем <%= code %> на фактический код
                    const finalHtml = html.replace('<%= code %>', response.data.code);
                    res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
                    res.end(finalHtml);
                });
            } else {
                // Если ни URL, ни код нет, обрабатываем как ошибку
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
});
app.get('/logout', async (req, res) => {
    const value = await valedTocen(req);
    if (!value) {
        return res.redirect('/');
    }
    const all = req.query.all === 'true';
    if(all){
        console.log("all");
    }
    deleteSessionToken(req.cookies.session_token);
    return res.redirect('/');
});
app.use((req, res) => {
    return res.redirect('/');
});
module.exports = app;