package DB

import (
	"context"
	"fmt"
	"log"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// регестрация/автаризация пользователя от github: | userGit данные типа UserGit
func DbGit(userGit UserGit) Response {
	newUser := UserMo{
		Name:   userGit.Name,
		Email:  userGit.Email,
		GitId:  userGit.UserID,
		YandID: "",
	}
	exists, logID, err := mondoChec("gitId", newUser.GitId)
	var res Response
	if err != nil {
		// Обработка ошибки
		fmt.Println("Ошибка:", err)
		res.Log, res.ID, res.Name = "ошибка", logID, ""
	} else if exists {
		fmt.Println("Пользователь с GitId найден")
		name, err := seePole("name", logID)
		if err != nil {
			fmt.Println("ошибка 32 DB")
		}
		res.Log, res.ID, res.Name = "Авторизован", logID, name
	} else {
		fmt.Println("Пользователь с GitId не найден")
		flag, logID, _ := mondoChec("email", newUser.Email)
		if flag {
			fmt.Println("Пользователь найден по почте янекса")
			replaceInfoUser(logID, "gitId", newUser.GitId)
			name, err := seePole("name", logID)
			if err != nil {
				fmt.Println("ошибка 43 DB")
			}
			res.Log, res.ID, res.Name = "Авторизован", logID, name
		} else {
			res.ID, _ = mondoWrite(newUser)
			name, err := seePole("name", logID)
			if err != nil {
				fmt.Println("ошибка 50 DB")
			}
			res.Log, res.Name = "зарегестрирован", name
		}
	}
	return res
}

// регестрация/автаризация пользователя от яндекс: | userYndex данные типа UserYndex
func DbYand(userYndex UserYndex) Response {
	newUser := UserMo{
		Name:   userYndex.Login,
		Email:  userYndex.DefaultEmail,
		GitId:  "",
		YandID: userYndex.ID,
	}
	exists, logID, err := mondoChec("yandID", newUser.YandID)
	var res Response
	if err != nil {
		// Обработка ошибки
		fmt.Println("Ошибка:", err)
		res.Log, res.ID, res.Name = "ошибка", logID, ""
	} else if exists {
		fmt.Println("Пользователь с YandID найден")
		name, err := seePole("name", logID)
		if err != nil {
			fmt.Println("ошибка 77 DB")
		}
		res.Log, res.ID, res.Name = "Авторизован", logID, name
	} else {
		fmt.Println("Пользователь с YandID не найден")
		flag, logID, _ := mondoChec("email", newUser.Email)
		if flag {
			fmt.Println("Пользователь найден по почте GitHub")
			replaceInfoUser(logID, "yandID", newUser.YandID)
			name, err := seePole("name", logID)
			if err != nil {
				fmt.Println("ошибка 88 DB")
			}
			res.Log, res.ID, res.Name = "Авторизован", logID, name
		} else {
			res.ID, _ = mondoWrite(newUser)
			name, err := seePole("name", logID)
			if err != nil {
				fmt.Println("ошибка 95 DB")
			}
			res.Log, res.Name = "зарегестрирован", name
		}
	}
	return res
}

// проверка существования пользователя: | base поле для проверки | value значение для проверки
func mondoChec(base string, value string) (bool, string, error) {
	collection := getCollection()

	// Создаем фильтр на основе переданного поля и значения
	filter := bson.M{base: value}

	var existingUser UserMo
	err := collection.FindOne(context.TODO(), filter).Decode(&existingUser)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return false, "", nil // Пользователь не найден
		}
		// Если произошла другая ошибка, возвращаем ее
		return false, "", fmt.Errorf("ошибка при поиске пользователя: %w", err)
	}

	// Если пользователь найден, возвращаем true
	return true, existingUser.ID.Hex(), nil
}

// регестрация пользователя: | newUser форма для добавления в DB
func mondoWrite(newUser UserMo) (string, error) {
	collection := getCollection()
	insertResult, err := collection.InsertOne(context.TODO(), newUser)
	if err != nil {
		return "err", err
	}
	id, _ := insertResult.InsertedID.(primitive.ObjectID)
	return id.Hex(), nil
}

// замена определёного поля: | id пользователя | base поле для изменения | value значение для изменения
func replaceInfoUser(id string, base string, value string) bool {
	collection := getCollection()
	objID, _ := primitive.ObjectIDFromHex(id)
	filter := bson.M{"_id": objID}
	if value == "" {
		return false
	}
	update := bson.M{"$set": bson.M{base: value}}
	_, err := collection.UpdateOne(context.TODO(), filter, update)
	if err != nil {
		fmt.Println(err)
		return false
	}
	fmt.Printf("документ обновлён: id: %s  | %s -> %s \n", id, base, value)
	return true
}

// посмотреть что лежит в поле: | base поле для просмотра | id у которого смотреть
func seePole(base string, id string) (string, error) {
	collection := getCollection()
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return "", err
	}
	filter := bson.M{"_id": objID}
	var result bson.M
	err = collection.FindOne(context.TODO(), filter).Decode(&result)
	if err != nil {
		return "", err
	}
	value, ok := result[base]
	if !ok {
		return "", nil
	}
	return value.(string), nil
}

// соеденение с MongoDB
var client *mongo.Client

// Подключение к MongoDB
func init() {
	serverAPI := options.ServerAPI(options.ServerAPIVersion1)
	opts := options.Client().ApplyURI("mongodb+srv://oruzni:1234@clusternum.6lw1y.mongodb.net/?retryWrites=true&w=majority&appName=ClusterNum").SetServerAPIOptions(serverAPI)
	var err error
	client, err = mongo.Connect(context.TODO(), opts)
	if err != nil {
		log.Fatal("нет доступа к DB")
		log.Fatal(err)
	}
	if err := client.Ping(context.TODO(), nil); err != nil {
		log.Fatal(err)
	}
	fmt.Println("Подключено к MongoDB!")
}

// конект к базе(users) с пользователями
func getCollection() *mongo.Collection {
	return client.Database("RegDB").Collection("users")
}

// Закрытие соеденения с MongoDB
func CloseDB() {
	if err := client.Disconnect(context.TODO()); err != nil {
		log.Fatal(err)
	}
	fmt.Println("Соединение с MongoDB закрыто.")
}
