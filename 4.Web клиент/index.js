const express = require("express");
const path = require("path");
const redis = require("redis");

const app = express();
const port = 3020;

// Middleware для обработки JSON
app.use(express.json());

// Подключение к Redis
const client = redis.createClient();

client
  .connect()
  .then(() => console.log("Подключено к Redis"))
  .catch((err) => console.error("Ошибка подключения к Redis:", err));

// Обработчик ошибок Redis
client.on("error", (err) => {
  console.error("Ошибка Redis: " + err);
});

// Эндпоинт для сохранения сессии
app.post("/saveSession", async (req, res) => {
  const { sessionToken, loginToken } = req.body;

  if (!sessionToken || !loginToken) {
    return res.status(400).json({ error: "Неполные данные" });
  }

  try {
    // Создаем значение для сессии
    const sessionData = {
      status: "Анонимный",
      loginToken,
    };

    // Сохраняем токен сессии как ключ, а статус пользователя и токен входа как значение
    await client.set(sessionToken, JSON.stringify(sessionData));
    console.log(`Сессия сохранена: ${sessionToken} ->`, sessionData);

    res.status(200).json({ message: "Сессия успешно сохранена" });
  } catch (err) {
    console.error("Ошибка при сохранении в Redis:", err);
    res.status(500).json({ error: "Ошибка сервера" });
  }
});

// Эндпоинты для статики
app.get("/", (req, res) => {
  res.sendFile("login.html", { root: path.join(__dirname, "public") });
});

app.get("/login", (req, res) => {
  res.sendFile("index.html", { root: path.join(__dirname, "public") });
});

app.get("/index", (req, res) => {
  res.sendFile("index.html", { root: path.join(__dirname, "public") });
});

app.get("/creating", (req, res) => {
  res.sendFile("creating.html", { root: path.join(__dirname, "public") });
});

app.get("/profile", (req, res) => {
  res.sendFile("profile.html", { root: path.join(__dirname, "public") });
});

// Запуск сервера
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
