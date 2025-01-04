// discipline.h
#ifndef DISCIPLINE_H
#define DISCIPLINE_H

#include <httplib.h>

void handle_create_discipline(const httplib::Request& req, httplib::Response& res);
void handle_get_discipline(const httplib::Request& req, httplib::Response& res);
nlohmann::json get_discipline_from_db(int discipline_id);

#endif // DISCIPLINE_H