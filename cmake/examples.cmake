
function (example_function_with_varargs ARG1 ARG2)
  #https://cmake.org/cmake/help/v3.0/module/CMakeParseArguments.html
  set(options FLAG_NAME_1 FLAG_NAME_2 FLAG_NAME_N)
  set(oneValueArgs SCALAR_NAME_1 SCALAR_NAME_2 SCALAR_NAME_N)
  set(multiValueArgs VEC_NAME_1 VEC_NAME_2 VEC_NAME_N)
  cmake_parse_arguments(MY "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

  message(STATUS "MY_VEC_NAME_1 = ${MY_VEC_NAME_1}")
  message(STATUS "MY_FLAG_NAME_1 = ${MY_FLAG_NAME_1}")
  message(STATUS "MY_SCALAR_NAME_1 = ${MY_SCALAR_NAME_1}")
endfunction ()


function(argn_example TARGET)
message("ARGC=\"${ARGC}\"")
message("ARGN=\"${ARGN}\"")
message("ARGV=\"${ARGV}\"")
message("ARGV0=\"${ARGV0}\"")
message("ARGV1=\"${ARGV1}\"")
endfunction()
add_custom_target(foo
COMMAND ls)
argn_example(foo core bitwriter)
# Results:
# ARGC="3"
# ARGN="core;bitwriter"
# ARGV="foo;core;bitwriter"
# ARGV0="foo"
# ARGV1="core"
