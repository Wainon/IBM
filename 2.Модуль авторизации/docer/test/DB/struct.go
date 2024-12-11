package DB

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

//да
//данные

// данные для OAuth Yndex
const (
	CLIENT_ID_Yndex     = "fba88c3d4b524c56a211c216d014ad93"
	CLIENT_SECRET_Yndex = "3d595570b6f44e69a932a2fec5d059f3" //скрыты а так в коде присутствуют
)

// данные для OAuth gitHub
const (
	CLIENT_ID_git     = "Ov23liWkHlsBA5CJzhKP"
	CLIENT_SECRET_git = "86abe30f2eb60c8eb83b55d78a08e3c810333e6e" //скрыты а так в коде присутствуют
)
const (
	SECRET = "Wkb5e69a95d783e6a08e3Hl"
)

//Yndex

// структура для user входящего через Yndex
type UserYndex struct {
	Login        string `json:"login"`
	DefaultEmail string `json:"default_email"`
	ID           string `json:"id"`
}

//gitHub

// структура для user входящего через gitHub
type UserGit struct {
	Name   string `json:"login"`
	Email  string `json:"email"`
	UserID string `json:"id"`
}

// структура принимающая даные с gitHub
type formGetInGitHub struct {
	Name   string `json:"login"`
	UserID int64  `json:"id"`
}

// структура принимающая email с gitHub
type EmailData struct {
	Email    string `json:"email"`
	Primary  bool   `json:"primary"`
	Verified bool   `json:"verified"`
}

//общее

// структура ответа на регестрацию автаризацию
type Response struct {
	Name string
	ID   string
	Log  string
}

// структура хранения в базе данных DB
type UserMo struct {
	ID     primitive.ObjectID `bson:"_id,omitempty"`
	Name   string             `bson:"name"`
	Email  string             `bson:"email"`
	Role   []string           `bson:"role"`
	Access []string           `bson:"access"`
}

// структура с токином запроса
type TokenInfo struct {
	TokenTime time.Time
	State     string
	TokenU    string
	TokenD    string
}

type Tokens struct {
	TokenU string
	TokenD string
}

// словарь для хранения токенов c токенами
var _tokensInfo = make(map[string]TokenInfo)
