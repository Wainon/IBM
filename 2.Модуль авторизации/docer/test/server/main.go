package main

import (
	"fmt"
	"net/http" // для сервера
	"test/db"
)

func main() {
	router := http.NewServeMux()
	router.HandleFunc("/", handleRoot)
	router.HandleFunc("/reg", db.MdbN) // Убедитесь, что MdbN экспортирована (с заглавной буквы)

	// Запускаем сервер и обрабатываем возможные ошибки
	fmt.Println("Запуск сервера на порту :8080")
	if err := http.ListenAndServe(":8080", router); err != nil {
		fmt.Printf("Ошибка при запуске сервера: %s\n", err)
	}
}

func handleRoot(rw http.ResponseWriter, _ *http.Request) {
	rw.Write([]byte("Привет от Cats!"))
}
