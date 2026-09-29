# header-only: interface target exposing the vendor/ root so consumers
# can include via <ankerl/unordered_dense.h>
add_library(unordered_dense INTERFACE)
add_library(vendor::unordered_dense ALIAS unordered_dense)

target_include_directories(unordered_dense INTERFACE ..)
