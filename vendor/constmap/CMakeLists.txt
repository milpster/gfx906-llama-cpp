set(TARGET vendor-constmap)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

add_library(${TARGET} STATIC
    constmap.c
    constmap.h
)

add_library(vendor::constmap ALIAS ${TARGET})

# disable warnings in 3rd party code
if (CMAKE_C_COMPILER_ID STREQUAL "MSVC")
    set(NO_WARN_FLAG /w)
else()
    set(NO_WARN_FLAG -w)
endif()
set_source_files_properties(constmap.c PROPERTIES COMPILE_OPTIONS ${NO_WARN_FLAG})

# expose the vendor/ root so consumers can include via "constmap/constmap.h"
target_include_directories(${TARGET} PUBLIC ..)
