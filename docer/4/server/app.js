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
// удаляем токен входа в redis> KEYS *
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
// обновление AccessToken
async function updateAccessToken(req){
    const sessionToken =req.cookies.session_token
    if(sessionToken==null){
        return false
    }
    const log = await requestToRedis(sessionToken);
    const logRedis = log.data;
    const authUrl = `http://localhost:8080/func/updateAccessToken?state=${logRedis.RefreshToken}`;
    try {
        const response = await axios.get(authUrl);
        //console.log(response.status);
        if (response.status === 200) {
            //console.log(response.data.AccessToken);
            const userData = {
                status: logRedis.status,
                AccessToken: response.data.AccessToken,
                RefreshToken: logRedis.RefreshToken
            };
            //console.log(userData);
            await deleteSessionToken(sessionToken);
            await redis.set(sessionToken, JSON.stringify(userData));
            return true
        }
    }catch (error) {
        console.error(error.response.status);
        return false
    }
}
//проверка автаризованости 
async function valedTocen(req){

    const sessionToken =req.cookies.session_token
    if(sessionToken==null){
        return false
    }
    //console.log(sessionToken);
    logRedis = await requestToRedis(sessionToken);
    //console.log(logRedis);
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
                        //console.log(userData);
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
        return res.redirect('/profile');
    }
    res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
    fs.readFile(path.join(__dirname, '../html/authPage.html'), 'utf8', (err, data) => {
            if (err) {
                res.writeHead(500, { 'Content-Type': 'text/plain;charset=utf-8' });
                 res.end('Ошибка сервера\n');
                return;
            }
            res.end(data);
    });
    
        
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
app.get('/profile', async (req, res) =>{
    const value = await valedTocen(req);
    if (!value) {
        return res.redirect('/');
    }
    res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
    fs.readFile(path.join(__dirname, '../html/profile.html'), 'utf8', (err, data) => {
            if (err) {
                res.writeHead(500, { 'Content-Type': 'text/plain;charset=utf-8' });
                res.end('Ошибка сервера\n');
                return;
            }
            res.end(data);
    });
});
app.get('/profile/get', async (req, res) =>{
    const value = await valedTocen(req);
    if (!value) {
        return res.redirect('/');
    }
    const id = req.query.id; 
    const logRedis = await requestToRedis(req.cookies.session_token)
    authUrl = `http://localhost:8000/req?type=UserDats&AccessToken=${logRedis.data.AccessToken}`;
    if (id) {
        authUrl = `http://localhost:8000/req?type=UserDats&AccessToken=${logRedis.data.AccessToken}&id=${id}`;
    }
    try {
        const response = await axios.get(authUrl);
        if (response.status === 200) {
            return response.data;
        }else if(response.status === 401) {
            console.log("обновленгие токина")
            const f = await updateAccessToken(req);
            if(!f){
                deleteSessionToken(req.cookies.session_token);
            }
            if(id){
                return res.redirect(`/profile/get?id=${id}`); 
            }
            return res.redirect('/profile/get'); 
        }
    } catch (error) {
        
        const userData = {
            name: 'Пользователь с ID ' + id,
            email: 'user' + id + '@example.com'
        };
        const disciplines = [
            { id: 1, name: 'Математика' },
            { id: 2, name: 'Физика' },
            { id: 3, name: 'Информатика' },
            { id: 4, name: 'Химия' }
        ];
        return res.json({ user: userData, disciplines: disciplines });
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
app.get('/func', async (req, res) => {
    const type = req.query.type;
    //console.log(type);
    
    if (!type) {
        res.writeHead(404, { 'Content-Type': 'text/plain;charset=utf-8' });
        res.end();
        return;
    }

    //const value = await valedTocen(req);
    if (!value) {
        res.writeHead(404, { 'Content-Type': 'text/plain;charset=utf-8' });
        res.end();
        return;
    }

    //console.log(value);
    const logRedis = await requestToRedis(req.cookies.session_token);
    let authUrl = '';

    if (type === "updateName") {
        const newName = req.query.newName;
        if (newName) {
            authUrl = `http://localhost:8000/req?type=updateName&AccessToken=${logRedis.data.AccessToken}&newName=${newName}`;
        } else {
            res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
            res.end();
            return;
        }
    } else {
        res.writeHead(404, { 'Content-Type': 'text/plain;charset=utf-8' });
        res.end();
        return;
    }

    try {
        const response = await axios.get(authUrl);
        //console.log(response.status);
        
        if (response.status === 200) {
            res.writeHead(200);
            res.end();
            return;
        }
    } catch (error) {
        if (error.response) {
            if (error.response.status === 401) {
                //console.log("Обновление токена");
                const f = await updateAccessToken(req);
                //console.log(f, " f");
                if (!f) {
                    deleteSessionToken(req.cookies.session_token);
                }
            } else {
                console.error(`Ошибка: ${error.response.status} - ${error.response.data}`);
            }
        } else if (error.request) {
            console.error("Ошибка запроса:", error.request);
        } else {
            console.error("Ошибка:", error.message);
        }
    } finally {
        if (!res.headersSent) {
            res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
            res.end();
        }
    }
});
app.get('/discipline', async (req, res) => {
    const value = await valedTocen(req);
    if (!value) {
        return res.redirect('/');
    }
    const id = req.query.id;
    if(id){
        res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' });
        fs.readFile(path.join(__dirname, '../html/discipline.html'), 'utf8', (err, data) => {
                if (err) {
                    res.writeHead(500, { 'Content-Type': 'text/plain;charset=utf-8' });
                    res.end('Ошибка сервера\n');
                    return;
                }
                res.end(data);
        });
    }

});
app.get('/discipline/get', async (req, res) => {
    console.log("/discipline/get");
    const value = await valedTocen(req);
    if (!value) {
        return res.redirect('/');
    }
    const id = req.query.id;
    console.log(id);
    if(id){
        const disciplineData = {
            name: "Программирование на JavaScript",
            teacher: "Иванов Иван Иванович",
            questions: [
                { id: 1, text: "Что такое переменная?" },
                { id: 2, text: "Как объявить функцию в JavaScript?" },
                { id: 3, text: "Что такое замыкание?" },
                { id: 4, text: "Как работает 'this' в JavaScript?" },
                { id: 5, text: "Что такое промисы?" }
            ]
        };
    
        return res.json(disciplineData);
    }
});
app.use((req, res) => {
    return res.redirect('/');
});
module.exports = app;