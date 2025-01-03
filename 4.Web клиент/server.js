// web_client.js

const redis = require("redis");
const express = require("express");
const path = require("path"); // Для статических файлов
const app = express();

// Создаем клиент для подключения к Redis
const redisClient = redis.createClient({
  host: "127.0.0.1", // Укажите актуальный хост Redis
  port: 6379, // Порт по умолчанию для Redis
});

redisClient.on("error", (err) => {
  console.error("Ошибка Redis:", err);
});

// Middleware для проверки сессионных токенов
app.use(async (req, res, next) => {
  const sessionToken = req.cookies ? req.cookies.sessionToken : null; // Считываем токен из cookies

  if (!sessionToken) {
    req.userStatus = "unknown"; // Если токен отсутствует, пользователь неизвестен
    return next();
  }

  try {
    const redisData = await redisClient.getAsync(sessionToken);
    if (!redisData) {
      req.userStatus = "unknown"; // Если данных в Redis нет, пользователь неизвестен
      return next();
    }

    const { status, accessToken, refreshToken } = JSON.parse(redisData);

    req.userStatus = status; // Устанавливаем статус пользователя
    req.accessToken = accessToken; // Устанавливаем Access токен
    req.refreshToken = refreshToken; // Устанавливаем Refresh токен

    next();
  } catch (error) {
    console.error("Ошибка чтения из Redis:", error);
    req.userStatus = "unknown"; // В случае ошибки считаем пользователя неизвестным
    next();
  }
});

// Устанавливаем статические файлы для веб-клиента
app.use(express.static(path.join(__dirname, "public")));

// Маршрут для главной страницы
app.get("/", (req, res) => {
  if (req.userStatus === "authorized") {
    res.sendFile(path.join(__dirname, "public", "dashboard.html")); // Отправляем страницу личного кабинета
  } else {
    res.sendFile(path.join(__dirname, "public", "login.html")); // Отправляем страницу входа
  }
});

// Маршрут для входа
app.get("/login", async (req, res) => {
  const { type } = req.query;

  if (!type) {
    return res.redirect("/"); // Если параметр type отсутствует, перенаправляем на главную
  }

  const sessionToken = generateSessionToken(); // Генерируем сессионный токен
  const loginToken = generateLoginToken(); // Генерируем токен входа

  const redisData = {
    status: "anonymous", // Устанавливаем статус "анонимный"
    loginToken, // Сохраняем токен входа
  };

  await redisClient.setAsync(sessionToken, JSON.stringify(redisData)); // Сохраняем данные в Redis
  res.cookie("sessionToken", sessionToken, { httpOnly: true }); // Отправляем сессионный токен в cookies

  // Перенаправляем на модуль авторизации
  res.redirect(`http://auth-module/login?token=${loginToken}`);
});

// Маршрут для выхода
app.get("/logout", async (req, res) => {
  const sessionToken = req.cookies ? req.cookies.sessionToken : null;

  if (sessionToken) {
    await redisClient.delAsync(sessionToken); // Удаляем сессионный токен из Redis
  }

  res.clearCookie("sessionToken"); // Удаляем cookie с сессионным токеном
  res.redirect("/"); // Перенаправляем на главную страницу
});

// Вспомогательные функции
function generateSessionToken() {
  return Math.random().toString(36).substring(2); // Генерация случайного токена сессии
}

function generateLoginToken() {
  return Math.random().toString(36).substring(2); // Генерация случайного токена входа
}

app.listen(3000, () => {
  console.log("Веб-клиент запущен на порту 3000");
});
