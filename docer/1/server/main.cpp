#include <iostream>
#include <string>
#include "req.h"
#include <httplib.h> 

using namespace httplib;

int main() {
	Server svr;
    svr.Get("/", base);             // Создаём сервер (пока-что не запущен)
	svr.Get("/req", req);    // Обработчик отвечающий на GET запрос к /sum
	svr.listen("0.0.0.0", 8000); // Запуск сервера на порту 8080
}