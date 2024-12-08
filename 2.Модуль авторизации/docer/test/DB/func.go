package DB

import (
	"encoding/json"
	"net/http"
)

// смена имени пользователя
func ReName(w http.ResponseWriter, r *http.Request) {
	newName := r.URL.Query().Get("newname")
	id := r.URL.Query().Get("id")
	status := replaceInfoUser(id, "name", newName)
	data := map[string]bool{"status": status}
	json.NewEncoder(w).Encode(data)
}
