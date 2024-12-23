// req.cpp
#include <string>
#include <jwt-cpp/jwt.h>
#include <iostream>
#include <iomanip> 
#include <httplib.h> 
#include <ctime>
#include <vector>

using namespace httplib;

const std::string SECRET = "Wkb5e69a95d783e6a08e3Hl";
bool validate_token(const std::string& token) {
    try {
        auto decoded_token = jwt::decode(token);

        auto verifier = jwt::verify()
            .allow_algorithm(jwt::algorithm::hs256{ SECRET });

        verifier.verify(decoded_token);

        if (decoded_token.has_payload_claim("expires_at")) {
            auto claim = decoded_token.get_payload_claim("expires_at");
            auto expires_at = claim.as_number(); 
            if (expires_at > std::chrono::system_clock::to_time_t(std::chrono::system_clock::now())) {
                return true;
            }
        }
    } catch (const std::exception& e) {
        std::cout << "Exception: " << e.what() << "\n";
    }
    return false;
}
std::vector<std::string> getAccess(const std::string& token) {
    std::vector<std::string> access; 
    try {
        auto decoded_token = jwt::decode(token);
        auto payload = decoded_token.get_payload_claim("access").as_array();
        if (!payload.empty()) {
            for (const auto& item : payload) {
                access.push_back(item.get<std::string>());
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Ошибка: " << e.what() << std::endl;
    }
    return access; 
}

void UserDats(const std::string& id){

}

void req(const Request& req, Response& res) {
    std::string token = req.has_param("AccessToken") ? req.get_param_value("AccessToken") : "";

    // Проверка валидности токена
    if (token=="" || !validate_token(token)) {
        res.status = 401;
        res.set_content("401", "text/plain");
        return;
    }
    std::vector<std::string> access = getAccess(token);
    for (const std::string& str : access) {
        std::cout << str << std::endl;
    }

    std::string type = req.has_param("type") ? req.get_param_value("type") : "";
    
    if (type == "UserDats") {
        std::string id = req.has_param("id") ? req.get_param_value("id") : "";
        if (id == "") {
            // UserDats(access, access[0]);
        } else {
            // UserDats(access, id);
        }
    }else if(type=="updateName"){
         res.status = 200; 
        res.set_content("404", "text/plain");
    }
     else {
        res.status = 404; 
        res.set_content("404", "text/plain");
    }

    res.status = 200; // Успешный ответ
    res.set_content("200", "text/plain");
}

void base(const Request& req, Response& res) {
    res.set_content("base", "text/plain");
}