cmake_minimum_required(VERSION 2.6)
project(DOFUS_SNIFFER)

set(${PROJECT_NAME}_MAJOR_VERSION 0)
set(${PROJECT_NAME}_MINOR_VERSION 1)
set(${PROJECT_NAME}_PATCH_LEVEL 0)

set(CMAKE_INSTALL_PREFIX /home/heero)

set(CMAKE_C_FLAGS "-std=c99 -Wall -Wextra -ansi")

# find python libs/headers
find_package(PythonLibs REQUIRED)

include_directories(${PYTHON_INCLUDE_DIRS})

add_library(dofussniff SHARED dofus.c)
target_link_libraries(dofussniff ${PYTHON_LIBRARIES})

install(TARGETS dofussniff DESTINATION lib)
install(FILES python/pcolors.py python/buffer.py python/main.py DESTINATION lib/python)
