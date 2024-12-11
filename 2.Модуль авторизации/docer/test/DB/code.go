package DB

import (
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"net/url"
	"text/template"
)

func OauthCode(w http.ResponseWriter, r *http.Request) {
	code := r.URL.Query().Get("code")
	TokenU := r.URL.Query().Get("TokenU")
	Vurl := url.Values{}
	baseURL := "http://localhost:8081/oauth/log"
	Vurl.Add("code", code)
	Vurl.Add("TokenU", TokenU)
	fullURL := fmt.Sprintf("%s?%s", baseURL, Vurl.Encode())
	resp, err := http.Get(fullURL)
	if err != nil {
		fmt.Printf("ошибка в принятии данных :%s", err)
	}
	defer resp.Body.Close()
	w.WriteHeader(http.StatusOK)
	w.WriteHeader(resp.StatusCode) // Set the status code from the response
	if _, err := io.Copy(w, resp.Body); err != nil {
		http.Error(w, "ошибка при копировании данных", http.StatusInternalServerError)
		return
	}
}
func getCodeAut(token string) (string, error) {
	baseURL := "http://localhost:8081/oauth"
	Vurl := url.Values{}
	Vurl.Add("token", token)
	fullURL := fmt.Sprintf("%s?%s", baseURL, Vurl.Encode())
	resp, err := http.Get(fullURL)
	if err != nil {
		fmt.Println("Запрос ошибка:", err)
		return "", err
	}
	defer resp.Body.Close() // Закрываем тело ответа после завершения работы с ним

	// Читаем тело ответа
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("ошибка чтения тела:", err)
		return "", err
	}
	return string(body), nil
}
func OauthCodeRes(w http.ResponseWriter, r *http.Request) {
	state := r.URL.Query().Get("state")
	code := r.URL.Query().Get("code")
	err := r.URL.Query().Get("err")
	if code != "" {
		T, err := DbAll(code, "")
		if err != nil {
			http.Error(w, "errorG", http.StatusUnauthorized)
			fmt.Print(err)
			return
		}
		if info, exists := _tokensInfo[state]; exists {
			info.State = "доступ получен"
			info.TokenD = T.TokenD
			info.TokenU = T.TokenU
			_tokensInfo[state] = info

		}
		w.WriteHeader(http.StatusOK)

		// Define the HTML template
		tmpl := `
			<!DOCTYPE html>
			<html lang="ru">
			<head>
				<meta charset="UTF-8">
				<title>Успешная авторизация</title>
			</head>
			<body>
				<h1>Авторизация прошла успешно!</h1>
				<p>Доступ предоставлен.</p>
				<a href="/">Вернуться в приложение</a>
			</body>
			</html>
		`

		// Parse the template
		t, err := template.New("response").Parse(tmpl)
		if err != nil {
			http.Error(w, "Ошибка при обработке шаблона", http.StatusInternalServerError)
			return
		}

		// Execute the template and write it to the response
		if err := t.Execute(w, nil); err != nil {
			http.Error(w, "Ошибка при выводе шаблона", http.StatusInternalServerError)
		}
		fmt.Print("OK CodeAut")
		return
	} else if err != "" {
		if info, exists := _tokensInfo[state]; exists {
			info.State = "в доступе отказано"
			_tokensInfo[state] = info
		}
		http.Error(w, err, http.StatusUnauthorized)
		return
	} else {
		if info, exists := _tokensInfo[state]; exists {
			info.State = "в доступе отказано"
			_tokensInfo[state] = info
		}
		http.Error(w, "Неудачная авторизация. в доступе отказано.", http.StatusUnauthorized)
	}
}
