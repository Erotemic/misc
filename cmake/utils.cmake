  # dependency extraction
  message(STATUS "BUILDSYSTEM_TARGETS = ${BUILDSYSTEM_TARGETS}")

  function(get_all_external_projects)
    get_cmake_property(_vars VARIABLES)
    foreach (_key ${_vars})
      message(STATUS "_key = ${_key}")
      if (TARGET ${_key})
        get_target_property(_is_set ${_key} _EP_IS_EXTERNAL_PROJECT)
        if (_is_set)
          message(STATUS "_key = ${_key}")
        endif()
      endif()
    endforeach()
  endfunction()
  get_all_external_projects()

  function(SAFE_ExternalProject_Get_Property name)
    foreach(var ${ARGN})
      string(TOUPPER "${var}" VAR)
      get_property(is_set TARGET ${name} PROPERTY _EP_${VAR} SET)
      if(NOT is_set)
        #message(FATAL_ERROR "External project \"${name}\" has no ${var}")
      endif()
      get_property(${var} TARGET ${name} PROPERTY _EP_${VAR})
      set(${var} "${${var}}" PARENT_SCOPE)
    endforeach()
  endfunction()


  foreach (_extern_proj ${_viame_external_projects})
    if (TARGET ${_extern_proj})
      get_target_property(_dep_check ${_extern_proj} _EP_IS_EXTERNAL_PROJECT)
      if(_dep_check EQUAL 1)
        SAFE_ExternalProject_Get_Property(${_extern_proj} DEPENDS)
        message(STATUS "${_extern_proj} DEPENDS = ${DEPENDS}")
      endif()
    endif()
  endforeach()


  #get_cmake_property(_vars VARIABLES)
  #foreach (_varname ${_vars})
  #  message(STATUS "_varname = ${_varname}")
  #  #if (_varname MATCHES "VIAME_FORCEBUILD_.*")
  #  #endif()
  #endforeach()


  set (_viame_external_projects
    burnout
    darknet
    fletch
    kwant
    kwiver
    py-faster-rcnn
    scallop_tk
    smqtk
    viame
    viva
    )
  ###
  # Prevent make from recompiling specific packages.
  # For developer convinience only, do not use.
  # Turning any of these off may make rebuild faster, but the build will fail
  # (posibly silently) if any changes are made to those packages
  ##
  foreach (_extern_proj ${_viame_external_projects})
    set (VIAME_FORCEBUILD_${_extern_proj} True)
  endforeach()
  #set (VIAME_FORCEBUILD_KWIVER True)
  #set (VIAME_FORCEBUILD_FLETCH True)
  #set (VIAME_FORCEBUILD_VIVA True)
  #set (VIAME_FORCEBUILD_BURNOUT True)
  #set (VIAME_FORCEBUILD_SMQTK True)

function (sprokit_symlink_install)
  # """
  # Mimics a sprokit_install, but will symlink each file in `FILES` directly to
  # the directory `DESTINATION`.  This should only be used for dynamic
  # languages like python
  # """

  # FIXME: this is not working for the python tests
  # should no_install be used?
  if (no_install)
    return()
  endif ()

  # MIMIC the signature of `install`
  set(options)
  set(oneValueArgs DESTINATION COMPONENT)
  set(multiValueArgs FILES)
  cmake_parse_arguments(MY "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

  foreach(source_fpath ${MY_FILES})
      # Build abspath of the destination file
      get_filename_component(fname ${source_fpath} NAME)
      set(dest_fpath "${CMAKE_INSTALL_PREFIX}/${MY_DESTINATION}/${fname}")

      message(STATUS "Symlink-Install")
      message(STATUS " * source_fpath = ${source_fpath}")
      message(STATUS " * dest_fpath = ${dest_fpath}")

      # References:
      # https://github.com/bro/cmake/blob/master/InstallSymlink.cmake
      install(CODE "
        execute_process(COMMAND \"${CMAKE_COMMAND}\" -E create_symlink
          ${source_fpath}
          ${dest_fpath})
      "
      #COMPONENT ${MY_COMPONENT}
      )
  endforeach()

endfunction ()


# FIXME: breaks in the case that {varname} should be set to FALSE whenever it
# is not relevant. Currently, if its cached value is true it will still use it.
function(advanced_option varname docstring default is_relevant)
  # Allows advanced options to be shown in the gui only when appropriate
  # Once an variable is set as CACHE INTERAL, it seems the only way to make it
  # visible in the gui again is to unset it.
  if (DEFINED ${varname})
    # Remember the previous value of the variable
    set(value ${${varname}})
    unset(${varname} CACHE)
  else()
    # Use the default on the first call or if the var has been externally unset
    set(value ${default})
  endif()

  if (${is_relevant})
    # Show the last known value of the variable, but only in advanced mode
    option(${varname} ${docstring} ${value})
    mark_as_advanced(${varname})
  else()
    # Keep the variable around in internal cache, but dont show it even in
    # advanced mode.
    set(${varname} ${value} CACHE INTERNAL ${docstring})
  endif()
endfunction()


function (sprokit_symlink_install)
  # """
  # Mimics a sprokit_install, but will symlink each file in `FILES` directly to
  # the directory `DESTINATION`.  This should only be used for dynamic
  # languages like python
  # """

  # FIXME: this is not working for the python tests
  # should no_install be used?
  if (no_install)
    return()
  endif ()

  # MIMIC the signature of `install`
  set(options)
  set(oneValueArgs DESTINATION COMPONENT)
  set(multiValueArgs FILES)
  cmake_parse_arguments(MY "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

  foreach(source_fpath ${MY_FILES})
      # Build abspath of the destination file
      get_filename_component(fname ${source_fpath} NAME)
      set(dest_fpath "${CMAKE_INSTALL_PREFIX}/${MY_DESTINATION}/${fname}")

      message(STATUS "Symlink-Install")
      message(STATUS " * source_fpath = ${source_fpath}")
      message(STATUS " * dest_fpath = ${dest_fpath}")

      # References:
      # https://github.com/bro/cmake/blob/master/InstallSymlink.cmake
      install(CODE "
        execute_process(COMMAND \"${CMAKE_COMMAND}\" -E create_symlink
          ${source_fpath}
          ${dest_fpath})
      "
      #COMPONENT ${MY_COMPONENT}
      )
  endforeach()




function (example_function_with_args_kwargs)
  set(options FLAG_NAME_1 FLAG_NAME_2 FLAG_NAME_N)
  set(oneValueArgs SCALAR_NAME_1 SCALAR_NAME_2 SCALAR_NAME_N)
  set(multiValueArgs VEC_NAME_1 VEC_NAME_2 VEC_NAME_N)
  cmake_parse_arguments(MY "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

  message(STATUS "MY_VEC_NAME_1 = ${MY_VEC_NAME_1}")
  message(STATUS "MY_FLAG_NAME_1 = ${MY_FLAG_NAME_1}")
  message(STATUS "MY_SCALAR_NAME_1 = ${MY_SCALAR_NAME_1}")
endfunction ()
