cmake_minimum_required(VERSION 3.1)

project(restclient-cpp)

set(SRC
    source/connection.cc
    source/helpers.cc
    source/restclient.cc
)

set(INC
    include/restclient-cpp/connection.h
    include/restclient-cpp/helpers.h
    include/restclient-cpp/restclient.h
    include/restclient-cpp/version.h
)

include_directories(include)

find_package(CURL REQUIRED)
if (CURL_FOUND)
    include_directories(${CURL_INCLUDE_DIR})
else(CURL_FOUND)
    message(FATAL_ERROR "Could not find the CURL library")
endif(CURL_FOUND)

add_library(restclient-cpp ${SRC} ${INC})

find_package(CURL)
message(STATUS "Found Curl include: ${CURL_INCLUDE_DIR}")
message(STATUS "Found Curl library: ${CURL_LIBRARIES}")
include_directories(${CURL_INCLUDE_DIR})
target_link_libraries(restclient-cpp ${CURL_LIBRARIES})
