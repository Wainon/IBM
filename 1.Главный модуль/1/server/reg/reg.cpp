#include <iostream>
#include <jwt-cpp/jwt.h>
#include <string>
#include <httplib.h>
#include <nlohmann/json.hpp>
#include <vector>
#include <postgresql/libpq-fe.h>
#include "../discipline/discipline.h"

using json = nlohmann::json;

	const std::string SECRET = "Wkb5e69a95d783e6a08e3Hl";

//Проверяет JWT токен
bool validate_jwt (std::string& token){
    try {
        // Декодируем токен
        auto decoded = jwt::decode(token);

        auto verifier = jwt::verify().allow_algorithm(jwt::algorithm::hs256{ SECRET });

        verifier.verify(decoded);

        // Получаем поле expires_at (expiration time)
        auto exp_claim = decoded.get_payload_claim("expires_at");

        // Преобразуем значение exp в std::chrono::system_clock::time_point
        auto exp_time = exp_claim.as_date();

        // Получаем текущее время
        auto now = std::chrono::system_clock::now(); 

        // Сравниваем текущее время с временем истечения токена
        
        return now < exp_time;
    } catch (const std::exception& e) {
        // Обработка исключения
        std::cerr << "JWT не прошел проверку потому что: " << e.what() << std::endl;
        return false;
    }
}

std::vector<std::string> id_vec(const std::string& token) {
    std::vector<std::string> access;

    try {
        // Декодируем токен
        auto decoded_token = jwt::decode(token);

        try{
        // Получаем claim "access"
            auto id_get = decoded_token.get_payload_claim("access");

            try {
                    // Попробуем извлечь данные как массив
                auto access_array = id_get.as_array(); // Это может выбросить исключение, если не массив
                    
                    // Добавляем все элементы массива в вектор
                for (const auto& id : access_array) {
                    access.push_back(id.get<std::string>());
                }
            } catch (const std::exception& e) {
                    std::cerr << "Error: The 'access' claim is not an array: " << e.what() << std::endl;
                    }
        }catch (const std::exception& e){
            std::cerr << "Error: Failed to retrieve 'access' claim: " << e.what() << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error JWT: " << e.what() << std::endl;
    }  

    return access;
}

// Разрешения из payload
bool has_permission (std::string& token, const std::string& req_permission){
    try{
        auto decoded_token = jwt::decode(token);

         // Извлекаем разрешения пользователя 
        auto permissions = decoded_token.get_payload_claim("permission").as_array();

        for(const auto& permission : permissions){
            if(permission.get<std::string>() == req_permission){
                return true;
            }
        }

        return false;
    }catch (const std::exception& e) {
        std::cerr << "JWT не прошел проверку потому что: " << e.what() << std::endl;
        return false;
    }
}

bool is_admin(const std::string& token){
    // try{
    //     auto decoded_token = jwt::decode(token);

    //     auto role = decoded_token.get_payload_claim("role").as_string();

    //     return role == "admin";
    // }
    // catch(const std::exception& e){
    //     std::cerr << "Error role: " << e.what() << std::endl;
    //     return false;
    // }

    return true;
}

void insertUser(const std::string& email, const std::string& name) {
    PGconn* conn = PQconnectdb("dbname=mydb user=postgres password=yourpassword host=localhost port=5432");

    if (PQstatus(conn) != CONNECTION_OK) {
        std::cerr << "Не удалось подключиться к базе данных: " << PQerrorMessage(conn) << std::endl;

        PQfinish(conn);
        return;
    }

    // Проверка существования пользователя по email
    const char* chek_sql = "SELECT email FROM users WHERE email = $1";
    const char* chek_params[1] = {email.c_str()};

    PGresult* chek_res = PQexecParams(conn, chek_sql, 1, nullptr, chek_params, nullptr, nullptr, 0);

    if (PQresultStatus(chek_res) != PGRES_TUPLES_OK){
        std::cerr << "Ошибка в проверке: " << PQerrorMessage(conn) << std::endl;
        PQclear(chek_res);
        PQfinish(conn);
        return;
    }

    if (PQntuples(chek_res) > 0){
        std::cerr << "Такой пользователь существует: " << email << std::endl;
        PQclear(chek_res);
        PQfinish(conn);
        return;
    }

    PQclear(chek_res);

    // SQL-запрос для вставки данных
    const char* insert_sql = "INSERT INTO users (username, email) VALUES ($1, $2)";
    
    // Параметры для запроса
    const char* insert_params[2] = {name.c_str(), email.c_str()};

    // Выполнение запроса
    PGresult* insert_res  = PQexecParams(conn, insert_sql, 2, nullptr, insert_params, nullptr, nullptr, 0);

    // Проверка результата
    if (PQresultStatus(insert_res ) != PGRES_COMMAND_OK) {
        std::cerr << "Ошибка при вставке: " << PQerrorMessage(conn) << std::endl;
    } else {
        std::cout << "Пользователь успешно вставлен!" << std::endl;
    }

    PQclear(insert_res);
    PQfinish(conn);
}

json get_UserData(const std::string& id) {
    // Пример использования httplib::Client для отправки внутреннего запроса
    httplib::Client cli("http://localhost:8080");
    json user_data;
    // Формируем URL для запроса данных пользователя
    std::string url = "/func/getinfouser?id=" + id;
    
    // Выполняем GET-запрос
    if (auto res = cli.Get(url.c_str())) {

        if (res->status == 200) {
            try {
                // Парсим ответ в JSON
                user_data["user"] = json::parse(res->body);

                std::cout << "Response body: " << res->body << std::endl; // Выводим ответ для отладки

                if (user_data.contains("error")){
                    std::cout << "Ошибка: " << user_data["error"] << std::endl;
                    return json();
                }

                // user_data = json::parse(res->body);

                // if (user_data.contains("email") && user_data.contains("name")) {
                //     std::string email = user_data["email"];
                //     std::string name = user_data["name"];
                    
                //     // Вставляем пользователя в базу данных
                //     insertUser (email, name);
                // } else {
                //     std::cerr << "Ошибка: Поля 'email' или 'name' отсутствуют в ответе." << std::endl;
                // }

            } catch (const json::parse_error& e) {
                std::cerr << "Ошибка парсинга JSON: " << e.what() << std::endl;
                return json();
            }
        } else {
            std::cerr << "Ошибка: HTTP статус " << res->status << std::endl;
            return json();
        }
    } else {
        std::cerr << "Ошибка: не удалось выполнить запрос." << std::endl;
        return json();
    }

    return user_data;
}

void handle_get_user_data (const httplib::Request& req, httplib::Response& res){

    // Получаем параметры из запроса
    std::string token = req.has_param("AccessToken") ? req.get_param_value("AccessToken") : "";

    if (token.empty() || !validate_jwt(token)){
        res.status = 401;
        res.set_content("401", "text/plain");
        return;
    }

    // Проверка разрешений (например, для получения данных требуется "read_data" разрешение)
    // if(!has_permission(token, "read_data")){
    //     res.status = 403;
    //     res.set_content("403", "text/plain");
    //     return;
    // }

    std::vector<std::string> ids = id_vec(token);

    std::string type = req.has_param("type") ? req.get_param_value("type") : ""; // Тип запроса

    json response;

    if (type == "UserDats") {
        std::string id = req.has_param("id") ? req.get_param_value("id") : ""; // ID запроса
        if(id == "null" || id == ""){
            response = get_UserData(ids[0]);
        }
        else{
            response = get_UserData(id);
        }
    } 
    else if (type == "createDiscipline") {
        handle_create_discipline(req, res);
        return;
    } 
    else if (type == "disciplineGet"){
        handle_get_discipline(req, res);
        return;
    }
    else {
        res.status = 400;
        res.set_content("400", "text/plain");
        return;
    }

    // Возвращаем результат
    res.status = 200;
    res.set_content(response.dump(), "application/json");
}