// req.cpp
#include <string>
#include <jwt-cpp/jwt.h>
#include <iostream>
#include <iomanip> 
#include <httplib.h> 
#include <ctime>

using namespace httplib;

const std::string SECRET = "Wkb5e69a95d783e6a08e3Hl";
bool validate_token(const std::string& token) {
    try {
        auto decoded_token = jwt::decode(token);
        auto verifier = jwt::verify()
            .allow_algorithm(jwt::algorithm::hs256{ SECRET });
        verifier.verify(decoded_token);
        return true; // Token is valid
    } catch (const std::exception& e) {
        return false;
    }
}

void req(const Request& req, Response& res) {
    std::string token = req.has_param("AccessToken") ? req.get_param_value("AccessToken") : "";

    // Проверка валидности токена
    if (token.empty() || !validate_token(token)) {
        res.status = 401;
        res.set_content("401", "text/plain");
        return;
    }

    // Декодирование токена
    auto decoded_token = jwt::decode(token);

    // Проверка разрешений тут где то

    // другой код

    res.status = 200; // Успешный ответ
    res.set_content("200", "text/plain");
    
}

void base(const Request& req, Response& res) {
    res.set_content("base", "text/plain");
}