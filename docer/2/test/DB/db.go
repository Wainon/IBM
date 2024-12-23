package DB

import (
	"context"
	"errors"
	"fmt"
	"log"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// автаризация github или yandex
func DbAll(email string, name string) (Tokens, error) {
	exists, logID, err := mondoChec("email", email)
	var access []string
	if err != nil {
		return Tokens{}, err
	}
	if exists {
		name, err = seePole("name", logID)
		if err != nil {
			return Tokens{}, err
		}
		access, err = seePoleA(logID)
		if err != nil {
			return Tokens{}, err
		}
		fmt.Println("Автаризован ползователь " + name + " id: " + logID)
	} else {
		newUser := UserMo{
			Name:   "Аноним | " + name,
			Email:  email,
			Role:   []string{"Студент"},
			Access: []string{},
		}
		name = "Аноним | " + name
		logID, err := mondoWrite(newUser)
		if err != nil {
			return Tokens{}, err
		}
		err = addInfoUser(logID,"access",logID)
		if err != nil {
			return Tokens{}, err
		}
		access, err = seePoleA(logID)
		if err != nil {
			return Tokens{}, err
		}
		fmt.Println("зарегестрирован ползователь " + name + " id: " + logID)
	}
	User := UserMo{
		Name:   name,
		Email:  email,
		Role:   []string{"Студент"},
		Access: access,
	}
	T := Tokens{
		TokenD: getTokenD(access),
		TokenU: getTokenU(User),
	}
	return T, nil
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
	return id.Hex(), nil //id и ошибка
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
// добавление значения в массив: | id пользователя | base поле для изменения | value значение для добавления
func addInfoUser(id string, base string, value string) error {
	collection := getCollection()
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return fmt.Errorf("ошибка преобразования ID: %w", err)
	}
	filter := bson.M{"_id": objID}
	if value == "" {
		return fmt.Errorf("значение не может быть пустым")
	}

	// Получаем текущий массив
	var user UserMo
	err = collection.FindOne(context.TODO(), filter).Decode(&user)
	if err != nil {
		return fmt.Errorf("ошибка получения документа: %w", err)
	}

	// Проверяем, существует ли значение в массиве
	exists := false
	switch base {
	case "access":
		for _, v := range user.Access {
			if v == value {
				exists = true
				break
			}
		}
	default:
		return fmt.Errorf("неизвестное поле для добавления: %s", base)
	}

	if exists {
		return fmt.Errorf("значение '%s' уже существует в поле '%s' для пользователя с id: %s", value, base, id)
	}

	// Если значение не существует, добавляем его
	update := bson.M{"$push": bson.M{base: value}} // Используем $push для добавления значения в массив
	_, err = collection.UpdateOne(context.TODO(), filter, update)
	if err != nil {
		return fmt.Errorf("ошибка обновления документа: %w", err)
	}
	return nil
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
func seePoleA(id string) ([]string, error) {
	collection := getCollection() // Убедитесь, что эта функция определена для возврата коллекции MongoDB
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return nil, err // Возвращаем nil вместо пустого среза для лучшей обработки ошибок
	}

	filter := bson.M{"_id": objID}
	var result bson.M
	err = collection.FindOne(context.TODO(), filter).Decode(&result)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return nil, nil // Возвращаем nil, если документ не найден
		}
		return nil, err // Возвращаем ошибку, если что-то другое пошло не так
	}

	value, ok := result["access"]
	if !ok {
		return nil, nil // Возвращаем nil, если поле "access" не существует
	}

	// Проверяем, является ли значение массивом строк
	accessArray, ok := value.(primitive.A)
	if !ok {
		return nil, errors.New("значение доступа не является массивом") // Возвращаем ошибку, если значение не массив
	}

	// Преобразуем массив в срез строк
	var accessStrings []string
	for _, v := range accessArray {
		strValue, ok := v.(string)
		if !ok {
			return nil, errors.New("значение в массиве доступа не является строкой") // Возвращаем ошибку, если элемент не строка
		}
		accessStrings = append(accessStrings, strValue)
	}

	// Проверка на пустой массив
	if len(accessStrings) == 0 {
		return nil, nil // Возвращаем nil, если массив пустой
	}

	return accessStrings, nil // Возвращаем массив строк
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
