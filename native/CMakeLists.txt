cmake_minimum_required(VERSION 3.25)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS "-Wall -Wextra")
set(CMAKE_CXX_FLAGS_RELEASE "-Ofast")

project(similiraptor VERSION 0.1.0)
include_directories(src)

set(SRC_SIMILIRAPTOR
        src/similiraptor.hpp
        src/core.hpp
        src/similiraptor.cpp)

add_library(similiraptor MODULE ${SRC_SIMILIRAPTOR})
target_link_libraries(similiraptor -static-libgcc -static-libstdc++)
set_target_properties(similiraptor PROPERTIES PREFIX "")
set_target_properties(similiraptor PROPERTIES VERSION ${PROJECT_VERSION})
set_target_properties(similiraptor PROPERTIES SOVERSION 1)
install(TARGETS similiraptor LIBRARY DESTINATION "${CMAKE_SOURCE_DIR}/../similiraptor")
