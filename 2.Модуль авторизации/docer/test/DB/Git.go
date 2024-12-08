package DB

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strconv"
	"strings"
)

// запрос на регестрацию/автаризацию
func OauthGit(w http.ResponseWriter, r *http.Request) {
	code := r.URL.Query().Get("code")
	var response Response
	if code != "" {
		accessToken := getAccessToken(code)
		userData := getUserData(accessToken)
		userData.Email = getUserEmail(accessToken)

		if userData.UserID == "" {
			response.ID = "0"
			response.Log = "ошибка токен устарел"
			fmt.Println("id: " + userData.UserID)
		} else {

			response = DbGit(userData)
			if response.ID == "" {
				fmt.Println(response.Log)
			} else {
				fmt.Println(response.Log + " id: " + response.ID)
			}
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
func getUserData(AccessToken string) UserGit {
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
