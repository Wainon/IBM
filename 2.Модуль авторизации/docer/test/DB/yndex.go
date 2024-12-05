package DB

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
)

type TokenRequest struct {
	Token string `json:"token"`
}

func HandleYndex(rw http.ResponseWriter, r *http.Request) {
	// Убедитесь, что метод запроса - POST
	if r.Method != http.MethodPost {
		http.Error(rw, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Читаем тело запроса
	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(rw, "Failed to read request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// Декодируем JSON
	var tokenRequest TokenRequest
	if err := json.Unmarshal(body, &tokenRequest); err != nil {
		http.Error(rw, "Invalid JSON", http.StatusBadRequest)
		return
	}
	//tokenRequest.Token

	rw.Header().Set("Content-Type", "application/json")
	response := map[string]string{"received_token": tokenRequest.Token}
	json.NewEncoder(rw).Encode(response)
}
