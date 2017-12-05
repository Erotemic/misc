#include <iostream>
#include <dlfcn.h>
#include <Python.h>
#include <stdio.h>
#include <elf.h>
#include <link.h>

void BAR(){
  std::cout << "caled BAR" << std::endl;
}

#define MACRO_STR_NAME(arg) #arg
#define MACRO_STR_VALUE(arg) MACRO_STR_NAME(arg)

#define MACRO_A MACRO_B
#define MACRO_B MACRO_A



int main(){
  /*
   cd ~/misc/tests/cpp

   g++ symbols.cxx -DFOO=BAR -std=c++11 -ldl && ./a.out

   g++ symbols.cxx  -DFOO=BAR -std=c++11 `python -m pybind11 --includes` -Wl,--no-as-needed -L`python-config --configdir` `python-config --libs` -ldl && ./a.out
   g++ symbols.cxx  -std=c++11 `python -m pybind11 --includes` -Wl,--no-as-needed -L`python-config --configdir` `python-config --libs` -ldl && ./a.out

   */

  BAR();

  #define FOO_VALUE #FOO

  std::cout << "MACRO_STR_NAME(FOO)  = " << MACRO_STR_NAME(FOO) << std::endl;
  std::cout << "MACRO_STR_VALUE(FOO) = " << MACRO_STR_VALUE(FOO) << std::endl;

  std::cout << "MACRO_STR_NAME(MACRO_A)  = " << MACRO_STR_NAME(MACRO_A) << std::endl;
  std::cout << "MACRO_STR_VALUE(MACRO_A) = " << MACRO_STR_VALUE(MACRO_A) << std::endl;

  std::cout << "MACRO_STR_NAME(MACRO_B)  = " << MACRO_STR_NAME(MACRO_B) << std::endl;
  std::cout << "MACRO_STR_VALUE(MACRO_B) = " << MACRO_STR_VALUE(MACRO_B) << std::endl;

  std::cout << "MACRO_STR_NAME(MACRO_C)  = " << MACRO_STR_NAME(MACRO_C) << std::endl;
  std::cout << "MACRO_STR_VALUE(MACRO_C) = " << MACRO_STR_VALUE(MACRO_C) << std::endl;

  std::cout << "MACRO_STR_NAME(FOO)  = " << MACRO_STR_NAME(FOO) << std::endl;
  std::cout << "MACRO_STR_VALUE(FOO) = " << MACRO_STR_VALUE(FOO) << std::endl;

  std::cout << "FOO_VALUE = " << MACRO_STR_VALUE(FOO_VALUE) << std::endl;
  std::cout << "MACRO_STR_VALUE(NOT_DEF_HERE) = " << MACRO_STR_VALUE(NOT_DEF_HERE) << std::endl;

  #ifdef FOO
    FOO();
    #else
    std::cout << "FOO not defined" << std::endl;
    #endif



    using std::cout;
    using std::cerr;

    const ElfW(Dyn) *dyn = _DYNAMIC;
    const ElfW(Dyn) *rpath = NULL;
    const char *strtab = NULL;
    for (; dyn->d_tag != DT_NULL; ++dyn) {
      if (dyn->d_tag == DT_RPATH) {
        rpath = dyn;
      } else if (dyn->d_tag == DT_STRTAB) {
        strtab = (const char *)dyn->d_un.d_val;
      }
    }

    std::cout << "rpath = " << rpath << std::endl;
    if (strtab != NULL && rpath != NULL) {
      printf("RPATH: %s\n", strtab + rpath->d_un.d_val);
    }

    //void* self_handle = dlopen(NULL, RTLD_LAZY);
    //void* self_handle = dlopen("a.out", RTLD_LAZY);
    //std::cout << "self_handle = " << self_handle << std::endl;
    //if (!self_handle) {
    //    cerr << "Cannot load library: " << dlerror() << '\n';
    //    return 1;
    //}

    //Dl_info self_info;
    //int result = dladdr(self_handle, &self_info);
    //std::cout << "result = " << result << std::endl;

    //std::cout << "self_info.dli_fname = " << self_info.dli_fname << std::endl;

    void* handle = dlopen("libpython3.5m.so", RTLD_LAZY);
    std::cout << "handle = " << handle << std::endl;
    if (!handle) {
        cerr << "Cannot load library: " << dlerror() << '\n';
        return 1;
    }

    // reset errors
    dlerror();

    // load the symbols
    //create_t* create_triangle = (create_t*) dlsym(handle, "create");
    //const char* dlsym_error = dlerror();
    //if (dlsym_error) {
    //    cerr << "Cannot load symbol create: " << dlsym_error << '\n';
    //    return 1;
    //}

  return 0;
}
