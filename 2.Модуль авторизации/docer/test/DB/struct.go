package DB

import "go.mongodb.org/mongo-driver/bson/primitive"
//да
//данные

// данные для OAuth Yndex
const (
	CLIENT_ID_Yndex     = "fba88c3d4b524c56a211c216d014ad93"
	CLIENT_SECRET_Yndex = "----------"//скрыты а так в коде присутствуют 
)

// данные для OAuth gitHub
const (
	CLIENT_ID_git     = "Ov23liWkHlsBA5CJzhKP"
	CLIENT_SECRET_git = "------------"//скрыты а так в коде присутствуют 
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
	Name string `json:"login"`
	ID   string `json:"id"`
	Log  string `json:"log"`
}

// структура хранения в базе данных DB
type UserMo struct {
	ID     primitive.ObjectID `bson:"_id,omitempty"`
	Name   string             `bson:"name"`
	Email  string             `bson:"email"`
	GitId  string             `bson:"gitId"`
	YandID string             `bson:"yandID"`
}
