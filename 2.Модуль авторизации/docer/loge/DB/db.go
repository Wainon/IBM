package DB

import (
	"context"
	"fmt"
	"log"
	"net/http"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type User struct {
	Name  string `bson:"name"`
	Email string `bson:"email"`
	Git   string `bson:"git"`
}

func MdbN(rw http.ResponseWriter, _ *http.Request) {
	// Настройка клиента MongoDB
	serverAPI := options.ServerAPI(options.ServerAPIVersion1)
	opts := options.Client().ApplyURI("mongodb+srv://oruzni:1234@clusternum.6lw1y.mongodb.net/?retryWrites=true&w=majority&appName=ClusterNum").SetServerAPIOptions(serverAPI)

	// Подключение к MongoDB
	client, err := mongo.Connect(context.TODO(), opts)
	if err != nil {
		log.Fatal(err)
	}
	defer func() {
		if err = client.Disconnect(context.TODO()); err != nil {
			log.Fatal(err)
		}
		fmt.Println("Отключено от MongoDB!")
	}()

	// Пинг базы данных
	if err := client.Database("admin").RunCommand(context.TODO(), bson.D{{"ping", 1}}).Err(); err != nil {
		log.Fatal(err)
	}
	fmt.Println("подключино к MongoDB!")

	// Выбор коллекции
	collection := client.Database("RegDB").Collection("users")

	// Создание нового пользователя
	newUser := User{
		Name:  "chakir",
		Email: "chakir@gmail.com",
		Git:   "https://github.com/zxchakir",
	}

	// Проверка на дубликат
	filter := bson.M{"email": newUser.Email}
	var existingUser User // Объявляем переменную для найденного пользователя

	err = collection.FindOne(context.TODO(), filter).Decode(&existingUser)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			// Если пользователь не найден, вставляем нового
			insertResult, err := collection.InsertOne(context.TODO(), newUser)
			if err != nil {
				log.Fatal(err)
			}
			// Выводим ID вставленного документа
			fmt.Println("Вставлен один документ: ", insertResult.InsertedID)
			rw.Write([]byte("Вставлен один документ"))
		} else {
			log.Fatalf("Произошла ошибка при проверке наличия существующего пользователя: %v", err)
		}
	} else {
		// Если пользователь найден, выводим его данные
		fmt.Printf("Пользователь  %s найдено по электронной почте: %s\n", existingUser.Name, existingUser.Email)
		rw.Write([]byte("Пользователь зарегестрирован по этой электронной почте"))
	}
}
