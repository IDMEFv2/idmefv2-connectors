cmake_minimum_required(VERSION 3.10)
project(IDMEFv2HelloWorldCpp VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(hello-world main.cpp)

target_compile_options(hello-world PRIVATE -Wall -Wextra -Wpedantic)
