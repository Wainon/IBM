package DB

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"
)

var authenticate struct {
	is_done bool
	code    string
}

type UserGit struct {
	Name        string
	Email       string
	UserID      int64
	AccessToken string
	Access      []int
}

type UserData struct {
	Id   int64  `json:"id"`
	Name string `json:"name"`
}

const (
	CLIENT_ID     = "Ov23liWkHlsBA5CJzhKP"
	CLIENT_SECRET = "44fc7ae2d1b5212f8201d187d436869c22ef7517"
)

func OauthGit(w http.ResponseWriter, r *http.Request) {
	code := r.URL.Query().Get("code") // Достаем временный код из запроса
	if code != "" {
		authenticate.is_done = true
		authenticate.code = code
		users := make(map[int64]*UserGit)
		accessToken := getAccessToken(authenticate.code)
		userData := getUserData(accessToken)

		if _, ok := users[userData.Id]; !ok {
			// Добавляем пользователя с дефолтными правами
			users[userData.Id] = &UserGit{
				Name:        userData.Name,
				Email:       "",
				UserID:      userData.Id,
				AccessToken: accessToken,
				Access:      []int{13},
			}

		}
		User := users[userData.Id]
		fmt.Println(User)
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel() // Отменяем контекст, когда функция завершится
		log, err := DbGit(ctx, *User)
		if err != nil {
			fmt.Println(err)
		} else {
			fmt.Println(log)
		}

	}
}

// Меняем временный код на токен доступа
func getAccessToken(code string) string {
	// Создаём http-клиент с дефолтными настройками
	client := http.Client{}
	requestURL := "https://github.com/login/oauth/access_token"

	// Добавляем данные в виде Формы
	form := url.Values{}
	form.Add("client_id", CLIENT_ID)
	form.Add("client_secret", CLIENT_SECRET)
	form.Add("code", code)

	// Готовим и отправляем запрос
	request, _ := http.NewRequest("POST", requestURL, strings.NewReader(form.Encode()))
	request.Header.Set("Accept", "application/json") // просим прислать ответ в формате json
	response, _ := client.Do(request)
	defer response.Body.Close()

	// Достаём данные из тела ответа
	var responsejson struct {
		AccessToken string `json:"access_token"`
	}
	json.NewDecoder(response.Body).Decode(&responsejson)
	return responsejson.AccessToken
}

// Получаем информацию о пользователе
func getUserData(AccessToken string) UserData {
	// Создаём http-клиент с дефолтными настройками
	client := http.Client{}
	requestURL := "https://api.github.com/user"

	// Готовим и отправляем запрос
	request, _ := http.NewRequest("GET", requestURL, nil)
	request.Header.Set("Authorization", "Bearer "+AccessToken)
	response, _ := client.Do(request)
	defer response.Body.Close()

	var data UserData
	json.NewDecoder(response.Body).Decode(&data)
	return data
}
