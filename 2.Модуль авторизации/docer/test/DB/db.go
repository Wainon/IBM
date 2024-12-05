package DB

import (
	"context"
	"fmt"
	"log"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type UserMo struct {
	Name   string `bson:"name"`
	Email  string `bson:"email"`
	GitId  int64  `bson:"gitId"`
	YandID string `bson:"YandID"`
}

func DbGit(ctx context.Context, userGit UserGit) (string, error) {
	newUser := UserMo{
		Name:   userGit.Name,
		Email:  userGit.Email, // Use email from userGit
		GitId:  userGit.UserID,
		YandID: "",
	}
	newUser.Email = "qwe@gmail.com"
	exists, err := mondoChec(ctx, "gitId", newUser.GitId)
	//exists, err := mondoChec(ctx, "email", newUser.Email)
	fmt.Println(newUser.GitId)
	fmt.Println(exists)
	if err != nil {
		// Обработка ошибки
		fmt.Println("Ошибка:", err)
		return "ошибка", err
	} else if exists {
		fmt.Println("Пользователь с GitId найден")
		return "Авторизован\n", nil
	} else {
		fmt.Println("Пользователь с GitId не найден")
		mondoWrite(ctx, newUser)

		return "зарегестрирован\n", nil
	}
}

func DbYand(UserGit) {

	return
}
func mondoChec(ctx context.Context, field string, value interface{}) (bool, error) {
	collection := getCollection()

	// Создаем фильтр на основе переданного поля и значения
	filter := bson.M{field: value}

	var existingUser UserMo
	err := collection.FindOne(context.TODO(), filter).Decode(&existingUser)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return false, nil // Пользователь не найден
		}
		// Если произошла другая ошибка, возвращаем ее
		return false, fmt.Errorf("ошибка при поиске пользователя: %w", err)
	}

	// Если пользователь найден, возвращаем true
	return true, nil
}

func mondoWrite(ctx context.Context, newUser UserMo) error {
	collection := getCollection()
	insertResult, err := collection.InsertOne(ctx, newUser)
	if err != nil {
		return err // Return error instead of logging
	}
	fmt.Println("Вставлен один документ: ", insertResult.InsertedID)
	return nil
}

var client *mongo.Client

func init() {
	serverAPI := options.ServerAPI(options.ServerAPIVersion1)
	opts := options.Client().ApplyURI("mongodb+srv://oruzni:1234@clusternum.6lw1y.mongodb.net/?retryWrites=true&w=majority&appName=ClusterNum").SetServerAPIOptions(serverAPI)
	var err error
	client, err = mongo.Connect(context.TODO(), opts)
	if err != nil {
		log.Fatal(err)
	}
	if err := client.Ping(context.TODO(), nil); err != nil {
		log.Fatal(err)
	}
	fmt.Println("Подключено к MongoDB!")
}
func getCollection() *mongo.Collection {
	return client.Database("RegDB").Collection("users")
}
