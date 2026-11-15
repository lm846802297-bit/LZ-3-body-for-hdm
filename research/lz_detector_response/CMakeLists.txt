cmake_minimum_required(VERSION 3.16)
project(LZ2026NREventResponse LANGUAGES CXX)

if(NOT DEFINED NEST_SOURCE_DIR OR NEST_SOURCE_DIR STREQUAL "")
  message(FATAL_ERROR "Set -DNEST_SOURCE_DIR=<path-to-pinned-NEST-checkout>")
endif()

if(NOT EXISTS "${NEST_SOURCE_DIR}/CMakeLists.txt")
  message(FATAL_ERROR "NEST_SOURCE_DIR does not contain CMakeLists.txt: ${NEST_SOURCE_DIR}")
endif()

# Build only the NEST core dependency required by the event-response driver.
set(BUILD_EXAMPLES OFF CACHE BOOL "Disable NEST examples" FORCE)
set(BUILD_GARFIELD OFF CACHE BOOL "Disable Garfield++ integration" FORCE)
set(BUILD_ROOT OFF CACHE BOOL "Disable ROOT integration" FORCE)
set(G4 OFF CACHE BOOL "Disable Geant4 integration" FORCE)

add_subdirectory("${NEST_SOURCE_DIR}" "${CMAKE_BINARY_DIR}/nest")

add_executable(
  lz_2026_nr_event_response
  cpp/lz_2026_nr_event_response.cpp
)

target_link_libraries(lz_2026_nr_event_response PRIVATE NESTCore)
target_compile_features(lz_2026_nr_event_response PRIVATE cxx_std_17)

if(MSVC)
  target_compile_definitions(NESTCore PRIVATE _USE_MATH_DEFINES)
  target_compile_definitions(lz_2026_nr_event_response PRIVATE _USE_MATH_DEFINES)
endif()
