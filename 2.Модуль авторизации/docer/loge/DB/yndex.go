package DB

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"
)

type RequestData struct {
	Key1 string `json:"key1"`
	Key2 string `json:"key2"`
}

type TokenValidationResponse struct {
	Valid     bool   `json:"valid"`
	UserID    string `json:"user_id"`
	ExpiresIn int    `json:"expires_in"`
}

func HandleYndex(rw http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		http.Error(rw, "Метод не разрешен", http.StatusMethodNotAllowed)
		return
	}

	// Читаем тело запроса
	body, err := io.ReadAll(req.Body)
	if err != nil {
		http.Error(rw, "Ошибка при чтении тела запроса", http.StatusBadRequest)
		return
	}
	defer req.Body.Close()

	// Декодируем JSON в структуру
	var data RequestData
	if err := json.Unmarshal(body, &data); err != nil {
		http.Error(rw, "Ошибка при декодировании JSON", http.StatusBadRequest)
		return
	}

	// Обработка полученных данных
	log.Printf("Полученные данные: %+v\n", data)

	// Здесь вы можете вызвать validateToken, если это необходимо
	// valid, userID, err := validateToken(data.Key1) // Пример использования

	// Отправляем ответ
	response := map[string]string{"status": "success", "message": "Данные успешно получены"}
	rw.Header().Set("Content-Type", "application/json")
	rw.WriteHeader(http.StatusOK)
	json.NewEncoder(rw).Encode(response)
}

func validateToken(token string) (bool, string, error) {
	url := fmt.Sprintf("https://api.yandex.ru/v1/validate_token?token=%s", token)

	// Создаем новый HTTP-запрос
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return false, "", err
	}

	// Устанавливаем таймаут для запроса
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	// Отправляем запрос
	resp, err := client.Do(req)
	if err != nil {
		return false, "", err
	}
	defer resp.Body.Close()

	// Проверяем статус ответа
	if resp.StatusCode != http.StatusOK {
		return false, "", fmt.Errorf("неверный статус ответа: %s", resp.Status)
	}

	// Декодируем JSON-ответ
	var validationResponse TokenValidationResponse
	if err := json.NewDecoder(resp.Body).Decode(&validationResponse); err != nil {
		return false, "", err
	}

	return validationResponse.Valid, validationResponse.UserID, nil
}