// handlers.h
#ifndef HANDLERS_H
#define HANDLERS_H
#include <httplib.h> 

using namespace httplib;

void req(const Request& req, Response& res);
void base(const Request& req, Response& res);

#endif // HANDLERS_H