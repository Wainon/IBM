const app = require('./app'); // Импортируем приложение из app.js

app.listen(3000, () => {
    console.log('Сервер запущен на http://localhost:3000');
});