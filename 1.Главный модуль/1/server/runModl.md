# runModl.sh
# Заходим в sudo
echo "Переход в режим суперпользователя..."
# su - << 'EOF'

# # Запуск PostgreSQL
# echo "Запуск PostgreSQL..."
# service postgresql start

# # Подключение к базе данных и выполнение SQL-скрипта
# echo "Подключение к базе данных 'mydb' и выполнение SQL-скрипта..."
# psql -d mydb -f /workspaces/web-server/main-code/1/database/user.sql

# # Выход из режима суперпользователя
# exit
# EOF

# Переход в директорию сборки
echo "Переход в директорию сборки..."
cd /workspaces/web-server/main-code/1/server/build

# Сборка проекта
echo "Сборка проекта..."
make

# Запуск сервера
echo "Запуск сервера..."
./web-server

# Ожидание завершения работы сервера
echo "Сервер завершил работу."
wait
