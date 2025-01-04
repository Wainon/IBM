#ifndef REG_H
#define REG_H

#include <string>
#include <vector>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

bool validate_jwt(std::string& token);
std::vector<std::string> id_vec(const std::string& token);
bool has_permission(std::string& token, const std::string& req_permission);
bool is_admin(const std::string& token);
void insertUser(const std::string& email, const std::string& name);
json get_UserData(const std::string& id);
void handle_get_user_data(const httplib::Request& req, httplib::Response& res);

#endif