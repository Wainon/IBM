package DB

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"text/template"
)

// запрос на регестрацию/автаризацию
func OauthYndex(w http.ResponseWriter, r *http.Request) {
	code := r.URL.Query().Get("code")
	state := r.URL.Query().Get("state")
	if code != "" {
		accessToken := getAccessTokenYndex(code)
		if accessToken == "" {
			if info, exists := _tokensInfo[state]; exists {
				info.State = "ошибка в получении токена"
				_tokensInfo[state] = info
			}
			http.Error(w, "ошибка в получении токена", http.StatusUnauthorized)
			return
		} else {
			userData := getUserDataYndex(accessToken)
			if userData.DefaultEmail != "" {
				T, err := DbAll(userData.DefaultEmail, userData.Login)
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
				
				// Загрузка HTML-шаблона из файла
				tmpl, err := template.ParseFiles("../success.html")
				if err != nil {
					http.Error(w, "Ошибка при обработке шаблона", http.StatusInternalServerError)
					return
				}

				// Выполнение шаблона и запись его в ответ
				if err := tmpl.Execute(w, nil); err != nil {
					http.Error(w, "Ошибка при выводе шаблона", http.StatusInternalServerError)
				}
				return
			} else {
				if info, exists := _tokensInfo[state]; exists {
					info.State = "ошибка не получена почта"
					_tokensInfo[state] = info
				}
				http.Error(w, "ошибка не получена почта", http.StatusUnauthorized)
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
func getAccessTokenYndex(code string) string {
	baseURL := url.Values{}
	baseURL.Set("grant_type", "authorization_code")
	baseURL.Set("code", code)
	baseURL.Set("client_id", CLIENT_ID_Yndex)
	baseURL.Set("client_secret", CLIENT_SECRET_Yndex)
	baseURL.Set("redirect_uri", "http://localhost:8080/oauth/yndex")

	resp, err := http.PostForm("https://oauth.yandex.ru/token", baseURL)
	if err != nil {
		return ""
	}
	defer resp.Body.Close()

	var tokenResponse struct {
		AccessToken string `json:"access_token"`
	}
	json.NewDecoder(resp.Body).Decode(&tokenResponse)

	return tokenResponse.AccessToken
}

// Получаем информацию о пользователе
func getUserDataYndex(accessToken string) *UserYndex {
	baseURL := "https://login.yandex.ru/info"
	Vurl := url.Values{}
	Vurl.Add("oauth_token", accessToken)
	Vurl.Add("format", "json")
	Vurl.Add("jwt_secret", CLIENT_SECRET_Yndex)
	fullURL := fmt.Sprintf("%s?%s", baseURL, Vurl.Encode())
	resp, err := http.Get(fullURL)
	if err != nil {
		fmt.Printf("ошибка в запосе данных :%s", err)
		return &UserYndex{}
	}
	defer resp.Body.Close()
	var user UserYndex
	if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
		fmt.Print("ошибка в чтении ответа данных о пользвотале json")
		return &UserYndex{}
	}
	return &user
}
