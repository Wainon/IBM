package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
)

// Глобальная переменная для проверки, что пользователь дал доступ
var authenticate struct {
	is_done bool
	code    string
}

// Данные GitHub приложения
const (
	CLIENT_ID     = "Ov23liWkHlsBA5CJzhKP"
	CLIENT_SECRET = "44fc7ae2d1b5212f8201d187d436869c22ef7517"
)

func main() {
	url := "https://github.com/login/oauth/authorize?client_id=" + CLIENT_ID

	// Выполняем GET-запрос
	resp, err := http.Get(url)
	if err != nil {
		fmt.Println("Ошибка при выполнении запроса:", err)
		return
	}
	// Проверяем статус ответа
	if resp.StatusCode != http.StatusOK {
		fmt.Printf("Ошибка: получен статус %d\n", resp.StatusCode)
		return
	}

	// Читаем тело ответа
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Ошибка при чтении тела ответа:", err)
		return
	}
	// Выводим тело ответа в виде строки
	fmt.Println(string(body))
}
