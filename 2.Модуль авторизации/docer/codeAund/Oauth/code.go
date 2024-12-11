package Oauth

import (
	"crypto/rand"
	"fmt"
	"io"
	"math/big"
	"net/http"
	"net/url"
	"time"

	"github.com/golang-jwt/jwt"
)

type CodeTokens struct {
	TokenTime time.Time
	token     string
}

const (
	SECRET = "Wkb5e69a95d783e6a08e3Hl"
)

// словарь для хранения токенов
var _CodeTokens = make(map[string]CodeTokens)

func CodeOauth(w http.ResponseWriter, r *http.Request) {
	// Получаем токен из запроса
	token := r.URL.Query().Get("token")
	if token == "" {
		http.Error(w, "токен пустой", http.StatusBadRequest)
		return
	}

	var code string
	// Генерируем уникальный код
	for {
		n, err := rand.Int(rand.Reader, big.NewInt(900000)) // Генерируем число от 0 до 899999
		if err != nil {
			http.Error(w, "ошибка генерации", http.StatusInternalServerError)
			return
		}
		code = fmt.Sprintf("%06d", n.Int64()+10000) // Ограничиваем диапазон от 10000 до 999999

		// Проверяем, существует ли код
		if _, exists := _CodeTokens[code]; !exists {
			break // Если код уникален, выходим из цикла
		}
	}

	// Сохраняем код и токен в словаре
	T := CodeTokens{
		TokenTime: time.Now().Add(1 * time.Minute),
		token:     token,
	}
	_CodeTokens[code] = T

	// Возвращаем сгенерированный код в ответе
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "%s", code)
}
func CodeLog(w http.ResponseWriter, r *http.Request) {
	code := r.URL.Query().Get("code")
	TokenU := r.URL.Query().Get("TokenU")
	falg := true
	// Проверка наличия кода
	Vurl := url.Values{}
	baseURL := "http://localhost:8080/oauth/code/res"
	if _, exists := _CodeTokens[code]; !exists {
		Vurl.Add("err", "неправелно указан код")
		falg = false
	}
	info := _CodeTokens[code]
	if !info.TokenTime.After(time.Now()) {
		delete(_CodeTokens, code)
		Vurl.Add("err", "время истекло")
		falg = false
	}
	email, err := uncoder(TokenU)
	if err != nil {
		Vurl.Add("err", "ошибка при чтении токена обновления")
		falg = false
	}
	fmt.Println(email)
	fmt.Println(falg)
	if falg {
		Vurl.Add("code", email)
		Vurl.Add("state", info.token)
	}
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
func uncoder(tokenString string) (string, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("неожиданный метод подписи: %v", token.Header["alg"])
		}
		return []byte(SECRET), nil
	})
	if err != nil {
		return "", fmt.Errorf("ошибка при парсинге токена: %w", err)
	}

	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		// Проверка срока действия токена
		if exp, ok := claims["expires_at"].(float64); ok {
			if time.Unix(int64(exp), 0).Before(time.Now()) {
				return "", fmt.Errorf("токен истек")
			}
		}
		if email, ok := claims["email"].(string); ok {
			return email, nil
		}
		return "", fmt.Errorf("поле email не найдено")
	}

	return "", fmt.Errorf("недействительный токен")
}
