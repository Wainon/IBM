package DB

import (
	"encoding/json"
	"net/http"
	"time"
	"fmt"
	"github.com/golang-jwt/jwt/v5"
)

// смена имени пользователя
func ReName(w http.ResponseWriter, r *http.Request) {
	newName := r.URL.Query().Get("newname")
	id := r.URL.Query().Get("id")
	status := replaceInfoUser(id, "name", newName)
	data := map[string]bool{"status": status}
	json.NewEncoder(w).Encode(data)
}
func ValedTocen(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	state := r.URL.Query().Get("state")
	if info, exists := _tokensInfo[state]; exists {
		if info.TokenTime.After(time.Now()) {
			response := map[string]string{
				"TokenD": info.TokenD,
				"TokenU": info.TokenU,
				"state":  info.State}
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(response)
			return
		}
		delete(_tokensInfo, state)
		w.WriteHeader(http.StatusUnauthorized)
		json.NewEncoder(w).Encode(map[string]string{"error": "время действия токена закончилось"})
		return
	}
	w.WriteHeader(http.StatusBadRequest)
	json.NewEncoder(w).Encode(map[string]string{"error": "не опознанный токен"})
}
// токен доступа
func getTokenD(Access []string) string {
	tokeExpiresAt := time.Now().Add(time.Minute * 1)

	JWT := jwt.MapClaims{
		"access":     Access,
		"expires_at": tokeExpiresAt.Unix(),
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, JWT)
	tokenString, _ := token.SignedString([]byte(SECRET))

	return tokenString
}
// токен обновления
func getTokenU(user UserMo) string {

	tokeExpiresAt := time.Now().Add(7 * 24 * time.Hour)

	JWT := jwt.MapClaims{
		"email":      user.Email,
		"expires_at": tokeExpiresAt.Unix(),
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, JWT)
	tokenString, _ := token.SignedString([]byte(SECRET))

	return tokenString
}

func UpdateAccessToken(w http.ResponseWriter, r *http.Request){
	tokenString := r.URL.Query().Get("state")
	//fmt.Println(tokenString)
	if tokenString == "" {
		http.Error(w, "Missing token", http.StatusUnauthorized)
		return
	}
	
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		// Проверяем метод подписи
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(SECRET), nil
	})

	if err != nil {
		http.Error(w, "Invalid token", http.StatusUnauthorized)
		return
	}

	// Проверяем, что токен действителен
	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		expiresAt := int64(claims["expires_at"].(float64))
		email := claims["email"].(string) 
		if time.Now().Unix() > expiresAt {
			http.Error(w, "Token expired", http.StatusUnauthorized)
			return // Токен истек
		}

		//
		_, logID, err := mondoChec("email", email)
		if err!=nil{
			http.Error(w, "Token expired", http.StatusUnauthorized)
			return // Токен истек
		}
		access, _ := seePoleA(logID)
		AccessToken:=getTokenD(access)
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]string{"AccessToken": AccessToken})
		return
	}

	http.Error(w, "Invalid token", http.StatusUnauthorized) // Токен недействителен
	return
}
