CMAKE_MINIMUM_REQUIRED(VERSION 3.1)

include(RezBuild)
include(RezRepository)
include(ExternalProject)


string(REGEX REPLACE "\\.r\\.[0-9]+" "" cuebot_version $ENV{REZ_BUILD_PROJECT_VERSION})

message("Building cuebot version: ${cuebot_version}")
message("CMake current directory: ${CMAKE_CURRENT_SOURCE_DIR}")

ExternalProject_add(
    cuebot
    URL ${url_cuebot}
    SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}
    PREFIX cuebot
    UPDATE_COMMAND ""
    CONFIGURE_COMMAND ""
    INSTALL_COMMAND ""
    BUILD_COMMAND ""
)

set(build_dir ${CMAKE_BINARY_DIR}/cuebot/src/cuebot/)

# Installing cuebot
install(
    CODE
    "execute_process(COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/gradlew build --project-dir ${CMAKE_CURRENT_SOURCE_DIR})"
)

install(
    DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/build"
    DESTINATION "${CMAKE_INSTALL_PREFIX}/cuebot"
    USE_SOURCE_PERMISSIONS
)

install(
    FILES
        bin/cuebot
    DESTINATION
        bin
    PERMISSIONS
        OWNER_READ OWNER_WRITE OWNER_EXECUTE
        GROUP_READ GROUP_EXECUTE
        WORLD_READ WORLD_EXECUTE
)

