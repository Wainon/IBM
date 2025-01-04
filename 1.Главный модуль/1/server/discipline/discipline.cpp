#include <iostream>
#include <httplib.h>
#include <nlohmann/json.hpp>
#include <postgresql/libpq-fe.h>
#include "../reg/reg.h" 

using json = nlohmann::json;

PGconn* connect_db() {
    PGconn* conn = PQconnectdb("dbname=mydb user=postgres password=yourpassword host=localhost port=5432");
    if (PQstatus(conn) != CONNECTION_OK) {
        std::cerr << "Database connection failed: " << PQerrorMessage(conn) << std::endl;
        PQfinish(conn);
        return nullptr;
    }
    
    std::cout << "Connected to database successfully!" << std::endl; // Отладочный вывод

    return conn;
}

json get_discipline_info(int discipline_id) {
    PGconn* conn = connect_db();
    if (!conn) {
        return json(); // Ошибка подключения
    }

    const char* query = R"(
        SELECT
            t.teacher_id AS teacher_id,
            d.discipline_name AS discipline_name,
            s.student_id AS student_id
        FROM
            teachers t
        JOIN
            teacher_disciplines td ON t.teacher_id = td.teacher_id
        JOIN
            disciplines d ON td.discipline_id = d.discipline_id
        LEFT JOIN
            student_disciplines sd ON d.discipline_id = sd.discipline_id
        LEFT JOIN
            students s ON sd.student_id = s.student_id
        WHERE
            d.discipline_id = $1
    )";
    const char* params[1] = { std::to_string(discipline_id).c_str() };

    PGresult* res = PQexecParams(conn, query, 1, nullptr, params, nullptr, nullptr, 0);

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        std::cerr << "SQL error: " << PQerrorMessage(conn) << std::endl;
        PQclear(res);
        PQfinish(conn);
        return json();
    }

    json discipline_get;
    //result["discipline_id"] = discipline_id;

    if (PQntuples(res) > 0) {
        // Извлекаем данные из результата
        discipline_get["discipline_name"] = PQgetvalue(res, 0, 1);
        discipline_get["teacher_id"] = PQgetvalue(res, 0, 0);
        //std::string teacher_name = PQgetvalue(res, 0, 2);
    }

    PQclear(res);
    PQfinish(conn);
    return discipline_get;
}

int insertDiscipline(const std::string& name, const std::string& teacher_id) {
    PGconn* conn = connect_db();
    if (!conn) {
        return -1; // Ошибка подключения
    }

    
    // Добавление преподавателя, если его нет
    const char* insert_teacher_query = "INSERT INTO teachers (teacher_id) VALUES ($1) ON CONFLICT (teacher_id) DO NOTHING";
    const char* insert_teacher_params[1] = { teacher_id.c_str() };

    PGresult* insert_res = PQexecParams(conn, insert_teacher_query, 1, nullptr, insert_teacher_params, nullptr, nullptr, 0);

    if (PQresultStatus(insert_res) != PGRES_COMMAND_OK) {
        std::cerr << "Failed to insert teacher: " << PQerrorMessage(conn) << std::endl;
        PQclear(insert_res);
        PQfinish(conn);
        return -1;
    }
    PQclear(insert_res);

    // Проверка существования teacher_id
    const char* check_teacher_query = "SELECT teacher_id FROM teachers WHERE teacher_id = $1";
    const char* check_params[1] = { teacher_id.c_str() };
    PGresult* check_res = PQexecParams(conn, check_teacher_query, 1, nullptr, check_params, nullptr, nullptr, 0);

    if (PQntuples(check_res) == 0) {
        std::cerr << "Teacher with ID " << teacher_id << " does not exist." << std::endl;
        PQclear(check_res);
        PQfinish(conn);
        return -1; // Преподаватель не найден
    }
    PQclear(check_res);

    // Вставляем дисциплину
    const char* query = "INSERT INTO disciplines (discipline_name) VALUES ($1) RETURNING discipline_id";
    const char* params[1] = { name.c_str() };

    PGresult* res = PQexecParams(conn, query, 1, nullptr, params, nullptr, nullptr, 0);

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        std::cerr << "SQL error: " << PQerrorMessage(conn) << std::endl;
        PQclear(res);
        PQfinish(conn);
        return -1;
    }

    int discipline_id = std::stoi(PQgetvalue(res, 0, 0));
    PQclear(res);

    // Связываем дисциплину с учителем
    const char* link_query = "INSERT INTO teacher_disciplines (teacher_id, discipline_id) VALUES ($1, $2)";
    const char* link_params[2] = { teacher_id.c_str(), std::to_string(discipline_id).c_str() };

    res = PQexecParams(conn, link_query, 2, nullptr, link_params, nullptr, nullptr, 0);

    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        std::cerr << "SQL error: " << PQerrorMessage(conn) << std::endl;
        PQclear(res);
        PQfinish(conn);
        return -1;
    }

    PQclear(res);
    PQfinish(conn);
    return discipline_id;
}

bool find_resolution(const std::vector<std::string>& id, const std::string& creat){
    for (auto creat_id : id){

        if (creat_id == creat){
            return true;
        }
    }
    return false;
}

// Обработчик создания дисциплины
void handle_create_discipline(const httplib::Request& req, httplib::Response& res) {

    static int last_id = 0;

    std::string token = req.has_param("AccessToken") ? req.get_param_value("AccessToken") : "";

    std::cout << "Токен" << std::endl;

    std::vector<std::string> ids = id_vec(token);

    if (!find_resolution(ids, "create_discipline")){
        res.status = 403;
        res.set_content("Unauthorized", "text/plain");
        return;
    }
    
    std::string name = req.has_param("name") ? req.get_param_value("name") : "";
    
    if (name.empty()) {
        //AccessToken доступа ids если 
        res.status = 200;
        res.set_content("Missing name", "text/plain");
        return;
    }

    int id = insertDiscipline(name, ids[0]);

    if (id == -1) {
        res.status = 500;
        res.set_content("Failed to create discipline", "text/plain");
        return;
    }

    last_id = id;


    json response;
    response["id"] = last_id;

    res.status = 200;
    std::cout << "200" << std::endl;
    res.set_content(response.dump(), "application/json");

    return;
}

// Обработчик получения дисциплины
void handle_get_discipline(const httplib::Request& req, httplib::Response& res) {
    
    std::string status_str = req.has_param("status") ? req.get_param_value("status") : "";
    std::string id_str = req.has_param("id") ? req.get_param_value("id") : "";
    
    int id = std::stoi(id_str);
    if (id <= 0) {
        res.status = 400;
        res.set_content("Invalid ID", "text/plain");
        return;
    }

    json discipline;
    json discipline_id = get_discipline_info(id);

    std::string teacher_id = discipline_id["teacher_id"];
    // Формируем JSON
    discipline["name"] = discipline_id["discipline_name"];
    discipline["teacher"] = {
        {"id", discipline_id["teacher_id"]},
        {"text", get_UserData(teacher_id)["user"]["name"]}
    };
    discipline["change"] = "true";
    discipline["recording"] = "true";
    
    if (status_str.empty() || status_str == "undefined"){
        discipline["questions"] = json::array();   //Массив ВОПРОСЫ
    }
    else if (status_str == "participants"){
            discipline["change"] = "true";
        //МАССИВ УЧАСТНИКИ ПРОСТО ОЛЕГ НАЗВАЛ questions
    }

    res.status = 200;
    res.set_content(discipline.dump(), "application/json");
}
