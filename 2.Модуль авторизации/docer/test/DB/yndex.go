package DB

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
)

// запрос на регестрацию/автаризацию
func OauthYndex(w http.ResponseWriter, r *http.Request) {
	code := r.URL.Query().Get("code")
	var response Response
	if code != "" {
		accessToken := getAccessTokenYndex(code)
		userData := getUserDataYndex(accessToken)
		if userData != nil {
			response = DbYand(*userData)
			if response.ID == "" {
				fmt.Println(response.Log)
			} else {
				fmt.Println(response.Log + " id: " + response.ID)
			}
		} else {
			response.ID = "0"
			response.Log = "ошибка токен устарел"
		}
	} else {
		response.ID = "0"
		response.Log = "хз какая ошибка"
	}
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(response); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
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
		return nil
	}
	defer resp.Body.Close()
	var user UserYndex
	json.NewDecoder(resp.Body).Decode(&user)
	return &user
}
