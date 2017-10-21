

function(parse_argn parent_argn)
  set(_local_argn "${ARGN}")
  # Use standard cmake_parse_arguments to define a new version with slightly
  # more compact syntax

  # Prefix each argn item with an underscore so it cant conflict with this function
  # Actually, we just cant do the differentiation.
  #set(_local_argn_safe)
  #foreach (item ${_local_argn})
  #  set(_local_argn_safe "${_local_argn_safe}" "_${item}")
  #endforeach()
  #message(STATUS "_local_argn_safe = ${_local_argn_safe}")


  set(_flags )
  set(_single PREFIX)
  set(_multi FLAGS SINGLE MULTI)
  cmake_parse_arguments(MY "${_flags}" "${_single}" "${_multi}" "${_local_argn}")

  if (NOT MY_PREFIX)
    set(MY_PREFIX "MY")
  endif()

  cmake_parse_arguments("${MY_PREFIX}" "${MY_FLAGS}" "${MY_SINGLE}" "${MY_MULTI}" "${parent_argn}")

  set(_parsed "${MY_FLAGS}" "${MY_SINGLE}" "${MY_MULTI}")
  foreach(vartype ${_parsed})
    foreach (varsuffix ${vartype})

      set(varname "${MY_PREFIX}_${varsuffix}")
      set(varval "${${varname}}")

      message(STATUS "SETTING : ${varname} = ${varval}")

      set(${varname} "${varval}" PARENT_SCOPE)

    endforeach()
  endforeach()

endfunction()


function (use_parse)
  message(STATUS "Call use_parse")
  message(STATUS "FUNC_ARGN = ${ARGN}")
  cmake_parse_arguments(MY "a;b" "c;d" "e;f;g" "${ARGN}")
  #parse_argn("${ARGN}"
  #  FLAGS a b
  #  SINGLE c d PREFIX
  #  MULTI e f g
  #  )
message(STATUS "MY_a = ${MY_a}")
message(STATUS "MY_c = ${MY_c}")
message(STATUS "MY_e = ${MY_e}")
endfunction()

use_parse(
  a
  c helloworld
  e 1 2 3
  )



# TRY TO MAKE A CMAKE-PORT OF PYTHON DEDENT
function(_dedent outvar text)
  # spaces only. no tabs allowed
  STRING(REGEX REPLACE ";" "\\\\;" _text "${text}")
  STRING(REGEX REPLACE "\n" ";" lines "${_text}")


  message(STATUS "text = ${text}")
  # remove whitespce only lines
  string(REGEX REPLACE "^[ \t]+$" "" "${text}" text)
  message(STATUS "text = ${text}")

  #string(REGEX MATCHALL "[a-zA-Z]+\ |[a-zA-Z]+$" SEXY_LIST "${text}")
  string(REPLACE "\n" ";" SEXY_LIST ${text})
  message(STATUS "SEXY_LIST = ${SEXY_LIST}")


  string(REGEX MATCHALL "([ \t]+)" indents "${text}")
  foreach (indent ${indents})
    message(STATUS "indent = \"${indent}\"")
  endforeach()
endfunction()


#_dedent(result "
#   My indented string
#    a;b;c;
#    lo;oks

#     like
#      this
#")
# message(STATUS "result = ${result}")

