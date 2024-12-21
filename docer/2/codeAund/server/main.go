package main

import (
	"fmt"
	"log"
	"net/http" // для сервера

	"example2.com/codeAund/Oauth"
)

func main() {
	router := http.NewServeMux()
	router.HandleFunc("/", handleRoot)
	router.HandleFunc("/oauth", Oauth.CodeOauth)
	router.HandleFunc("/oauth/log", Oauth.CodeLog)
	// Запускаем сервер и обрабатываем возможные ошибки
	log.Println("Запуск сервера на порту :8081")
	if err := http.ListenAndServe(":8081", router); err != nil {
		fmt.Printf("Ошибка при запуске сервера: %s\n", err)
	}
}

func handleRoot(rw http.ResponseWriter, _ *http.Request) {
	rw.Write([]byte("просто корень нечего нет"))
}
