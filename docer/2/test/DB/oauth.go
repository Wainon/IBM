package DB

import (
	"net/http"
	"time"
)

// формирование авторизации
func Oauth(w http.ResponseWriter, r *http.Request) {
	state := r.URL.Query().Get("state")
	Type := r.URL.Query().Get("type")
	var URL string
	w.Header().Set("Content-Type", "application/json")
	if state == "" {
		URL = "неуказан state"
	} else if Type == "git" {
		URL = "https://github.com/login/oauth/authorize?scope=user:email&client_id=Ov23liWkHlsBA5CJzhKP&state=" + state
		cratTocenInfo(state)
	} else if Type == "yndex" {
		cratTocenInfo(state)
		URL = "https://oauth.yandex.ru/authorize?response_type=code&client_id=fba88c3d4b524c56a211c216d014ad93&state=" + state
	} else if Type == "code" {
		cratTocenInfo(state)
		URL, err := getCodeAut(state)
		if err != nil {
			http.Error(w, "Ошибка при запросе кода", http.StatusInternalServerError)
		}
		response := `{"code": "` + URL + `"}`
		w.Write([]byte(response))
		return
	} else {
		URL = "не верные данные"
	}
	response := `{"URL": "` + URL + `"}`
	w.Write([]byte(response))
}

// формирует структуру из 2 полей: Устареет через: текущее время + 5 минут и Статус ответа от пользователя
func cratTocenInfo(state string) {
	// Устанавливаем время истечения токена (текущее время + 5 минут)
	expiresAt := time.Now().Add(5 * time.Minute)
	// Создаем структуру TokenInfo
	tokenInfo := TokenInfo{
		TokenTime: expiresAt,
		State:     "не получен",
	}
	_tokensInfo[state] = tokenInfo
}
