cmake_minimum_required(VERSION 3.15)
project(TextProcessor)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Threads package for pthread support
find_package(Threads REQUIRED)

# Main executable with phishing features and threading
add_executable(text_processor
    src/main.cpp
    src/phishing_features.cpp
    src/request_handler.cpp
)

# Link pthread library
target_link_libraries(text_processor PRIVATE Threads::Threads)

# Compiler warnings
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(text_processor PRIVATE -Wall -Wextra -pedantic)
endif()

# Install target
install(TARGETS text_processor DESTINATION bin)
