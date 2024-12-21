

# Переход в директорию server и запуск main.go
cd 2/codeAund/server
go run main.go &  # Запускаем в фоновом режиме
# Переход в директорию test и запуск main.go
cd ../../test/server
go run main.go &  # Запускаем в фоновом режиме
# Ожидание завершения всех фоновых процессов

wait