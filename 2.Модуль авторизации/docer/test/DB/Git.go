package DB

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"text/template"
)

// запрос на регестрацию/автаризацию
func OauthGit(w http.ResponseWriter, r *http.Request) {
	code := r.URL.Query().Get("code")
	state := r.URL.Query().Get("state")
	if code != "" {
		accessToken := getAccessToken(code)
		if accessToken == "" {
			if info, exists := _tokensInfo[state]; exists {
				info.State = "ошибка в обене токена"
				_tokensInfo[state] = info
			}
			http.Error(w, "ошибка в обене токена", http.StatusUnauthorized)
			return
		} else {
			userGit := getuserGit(accessToken)
			userGit.Email = getUserEmail(accessToken)

			if userGit.Email != "" {
				T, err := DbAll(userGit.Email, userGit.Name)
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
				return
			} else {
				if info, exists := _tokensInfo[state]; exists {
					info.State = "токен устарел"
					_tokensInfo[state] = info
				}
				http.Error(w, "токен устарел", http.StatusUnauthorized)
				return
			}
		}
	} else {
		if info, exists := _tokensInfo[state]; exists {
			info.State = "в доступе отказано"
			_tokensInfo[state] = info
		}
		http.Error(w, "Неудачная авторизация. в доступе отказано.", http.StatusUnauthorized)
	}

}

// Меняем временный код на токен доступа
func getAccessToken(code string) string {
	client := http.Client{}
	requestURL := "https://github.com/login/oauth/access_token"

	form := url.Values{}
	form.Add("client_id", CLIENT_ID_git)
	form.Add("client_secret", CLIENT_SECRET_git)
	form.Add("code", code)

	request, _ := http.NewRequest("POST", requestURL, strings.NewReader(form.Encode()))
	request.Header.Set("Accept", "application/json")
	response, err := client.Do(request)
	if err != nil {
		fmt.Printf("ошибка в запосе токена :%s", err)
		return ""
	}
	defer response.Body.Close()

	var responsejson struct {
		AccessToken string `json:"access_token"`
	}
	json.NewDecoder(response.Body).Decode(&responsejson)
	return responsejson.AccessToken
}

// Получаем информацию о пользователе
func getuserGit(AccessToken string) UserGit {
	client := http.Client{}
	baseURL := "https://api.github.com/user"

	request, _ := http.NewRequest("GET", baseURL, nil)
	request.Header.Set("Authorization", "Bearer "+AccessToken)
	response, err := client.Do(request)
	if err != nil {
		fmt.Printf("ошибка в запосе данных пользователя :%s\n", err)
		return UserGit{}
	}
	defer response.Body.Close()
	var data formGetInGitHub
	if err := json.NewDecoder(response.Body).Decode(&data); err != nil {
		fmt.Printf("ошибка в считывании данных о пользователе json: %s\n", err)
	}
	var res UserGit
	res.Name = data.Name
	res.UserID = strconv.FormatInt(data.UserID, 10)
	return res
}

// Получаем адреса электронной почты пользователя
func getUserEmail(AccessToken string) string {
	client := http.Client{}
	requestURL := "https://api.github.com/user/emails"

	request, _ := http.NewRequest("GET", requestURL, nil)
	request.Header.Set("Authorization", "Bearer "+AccessToken)
	response, err := client.Do(request)
	if err != nil {
		fmt.Printf("ошибка в запосе почты :%s\n", err)
		return ""
	}
	defer response.Body.Close()

	var emails []EmailData
	if err := json.NewDecoder(response.Body).Decode(&emails); err != nil {
		fmt.Printf("ошибка в считывании данных  emails json: %s\n", err)
	}

	return emails[0].Email
}
