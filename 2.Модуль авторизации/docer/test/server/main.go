package main

import (
	"fmt"
	"log"
	"net/http" // для сервера

	"example.com/test/DB"
)

func main() {
	router := http.NewServeMux()
	router.HandleFunc("/", handleRoot)
	router.HandleFunc("/oauth/git", DB.OauthGit)
	router.HandleFunc("/oauth/yndex", DB.OauthYndex)
	router.HandleFunc("/rename", DB.ReName)
	// Запускаем сервер и обрабатываем возможные ошибки
	log.Println("Запуск сервера на порту :8080")
	if err := http.ListenAndServe(":8080", router); err != nil {
		fmt.Printf("Ошибка при запуске сервера: %s\n", err)
	}
	defer DB.CloseDB()
}

func handleRoot(rw http.ResponseWriter, _ *http.Request) {
	rw.Write([]byte("Привет от Cats!"))
}
