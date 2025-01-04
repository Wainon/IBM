#include <iostream>
#include <httplib.h>
#include <postgresql/libpq-fe.h>
#include "reg.h" // Подключаем заголовочный файл
#include "../discipline/discipline.h"

int main(){
    httplib::Server svr;

    svr.Get("/req", handle_get_user_data); // Получение данных

    //Как я помню нужно запустить сервер на поруту 8000 так что вот 
    std::cout << "Север запущен от http://localhost:8000" << std::endl;
    svr.listen("0.0.0.0", 8000);

    return 0;
}
