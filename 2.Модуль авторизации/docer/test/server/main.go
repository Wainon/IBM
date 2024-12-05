package main

import (
	"fmt"
	"net/http" // для сервера

	"example.com/test/DB"
)

func main() {
	router := http.NewServeMux()
	router.HandleFunc("/", handleRoot)
	router.HandleFunc("/reg", DB.MdbN) //потом убрать
	router.HandleFunc("/oauth/git", DB.OauthGit)
	// Запускаем сервер и обрабатываем возможные ошибки
	fmt.Println("Запуск сервера на порту :8080")
	if err := http.ListenAndServe(":8080", router); err != nil {
		fmt.Printf("Ошибка при запуске сервера: %s\n", err)
	}
}

func handleRoot(rw http.ResponseWriter, _ *http.Request) {
	rw.Write([]byte("Привет от Cats!"))
}
