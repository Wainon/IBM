package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
)

func main() {
	// Первый запрос: POST
	baseURL := "http://localhost:8080/oauth"

	Vurl := url.Values{}
	Vurl.Add("type", "git") // Убедитесь, что этот параметр корректен для вашего случая
	Vurl.Add("state", "123qqwe")

	// Используем PostForm для отправки POST-запроса
	resp, err := http.PostForm(baseURL, Vurl)
	if err != nil {
		log.Fatalf("Ошибка при выполнении запроса: %v", err)
	}
	defer resp.Body.Close() // Закрываем тело ответа после чтения

	// Проверяем статус ответа
	if resp.StatusCode != http.StatusOK {
		log.Fatalf("Запрос завершился с ошибкой: %s", resp.Status)
	}

	// Читаем тело ответа
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatalf("Ошибка при чтении тела ответа: %v", err)
	}

	// Выводим результат в консоль
	fmt.Println("Ответ на POST-запрос:", string(body))

	// Второй запрос: GET
	getBaseURL := "http://localhost:8080/oauth/git"
	getVurl := url.Values{}
	getVurl.Add("code", "Ov23liWkHlsBA5CJzhKP")
	fullURL := fmt.Sprintf("%s?%s", getBaseURL, getVurl.Encode())

	resp, err = http.Get(fullURL)
	if err != nil {
		log.Fatalf("Ошибка при выполнении GET-запроса: %v", err)
	}
	defer resp.Body.Close() // Закрываем тело ответа после чтения

	// Проверяем статус ответа
	if resp.StatusCode != http.StatusOK {
		log.Fatalf("GET-запрос завершился с ошибкой: %s", resp.Status)
	}

	// Читаем тело ответа
	body, err = ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatalf("Ошибка при чтении тела ответа: %v", err)
	}

	// Выводим результат в консоль
	fmt.Println("Ответ на GET-запрос:", string(body))
}