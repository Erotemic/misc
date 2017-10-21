set (PYTHON_EXECUTABLE "python")


###
# Removes common indentation from a block of text to produce code suitable for
# setting to `python -c`, or using with pycmd. This allows multiline code to be
# nested nicely in the surrounding code structure.
#
# This function respsects PYTHON_EXECUTABLE if it defined, otherwise it uses
# `python` and hopes for the best.
function(dedent outvar text)
  # Use PYTHON_EXECUTABLE if it is defined, otherwise default to python
  if ("${PYTHON_EXECUTABLE}" STREQUAL "")
    set(_python_exe "python")
  else()
    set(_python_exe "${PYTHON_EXECUTABLE}")
  endif()
  set(_fixup_cmd "import sys; from textwrap import dedent; print(dedent(sys.stdin.read()))")
  execute_process(
    COMMAND echo "${text}"
    COMMAND "${PYTHON_EXECUTABLE}" -c "${_fixup_cmd}"
    #INPUT_FILE "${text}"
    RESULT_VARIABLE _dedent_exitcode
    OUTPUT_VARIABLE _dedent_text)
  if(NOT ${_dedent_exitcode} EQUAL 0)
    message(ERROR " Failed when executing code to remove extra indentation: \n\"\"\"\n${_fixup_cmd}\n\"\"\"
    Python dedent failed with error code: ${_dedent_exitcode}")
    message(FATAL_ERROR " Python dedent failed with error code: ${_dedent_exitcode}")
  endif()
  # Remove supurflous newlines (artifacts of print)
  string(STRIP "${_dedent_text}" _dedent_text)
  set(${outvar} "${_dedent_text}" PARENT_SCOPE)
endfunction()


###
# Private helper function to execute `python -c "<cmd>"`
#
# Runs a python command and populates an outvar with the result of stdout.
# Common indentation in the text of `cmd` is removed before the command is
# executed, so the caller does not need to worry about indentation issues.
#
# This function respsects PYTHON_EXECUTABLE if it defined, otherwise it uses
# `python` and hopes for the best.
function(pycmd outvar cmd)
  dedent(_dedent_cmd "${cmd}")
  # Use PYTHON_EXECUTABLE if it is defined, otherwise default to python
  if ("${PYTHON_EXECUTABLE}" STREQUAL "")
    set(_python_exe "python")
  else()
    set(_python_exe "${PYTHON_EXECUTABLE}")
  endif()
  # run the actual command
  execute_process(
    COMMAND "${PYTHON_EXECUTABLE}" -c "${_dedent_cmd}"
    RESULT_VARIABLE _exitcode
    OUTPUT_VARIABLE _output)
  if(NOT ${_exitcode} EQUAL 0)
    message(ERROR " Failed when running python code: \"\"\"\n${_dedent_cmd}\n\"\"\"")
    message(FATAL_ERROR " Python command failed with error code: ${_exitcode}")
  endif()
  # Remove supurflous newlines (artifacts of print)
  string(STRIP "${_output}" _output)
  set(${outvar} "${_output}" PARENT_SCOPE)
endfunction()


if (TRUE)
  dedent(result "
     My indented string
      a;b;c;
      lo;oks

       like
        this
  ")
  message(STATUS "result = ${result}")

  pycmd(result "print('hello world')")

    pycmd(result "
      import logging
      print(logging)
      print(logging)
    ")

  message(STATUS "result = ${result}")
endif()
