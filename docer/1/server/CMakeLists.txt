cmake_minimum_required(VERSION 3.10)

# Укажите путь к vcpkg
set(CMAKE_TOOLCHAIN_FILE "../vcpkg/scripts/buildsystems/vcpkg.cmake")

project(MyServer)

include_directories("../vcpkg/installed/x64-linux/include")
# Добавьте исполняемый файл
add_executable(main main.cpp req.cpp)

# Укажите зависимости
find_package(jwt-cpp REQUIRED)


# Связываем библиотеки
target_link_libraries(main jwt-cpp::jwt-cpp  pthread)