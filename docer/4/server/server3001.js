const app = require('./app'); // Импортируем приложение из app.js

app.listen(3001, () => {
    console.log('Сервер запущен на http://localhost:3001');
});