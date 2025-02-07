cmake_minimum_required(VERSION 3.10)
project(DOU_Blockchain VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(OpenSSL REQUIRED)

# Include directories
include_directories(include)

# Source files
set(SOURCES 
    src/message.cpp
    src/reward_system.cpp
    src/spam_prevention.cpp
    src/validator.cpp
    src/main.cpp
)

# Create executable
add_executable(dou_blockchain ${SOURCES})

# Link libraries
target_link_libraries(dou_blockchain 
    OpenSSL::SSL 
    OpenSSL::Crypto
)

# Optional: Add testing
enable_testing()
add_subdirectory(tests)
