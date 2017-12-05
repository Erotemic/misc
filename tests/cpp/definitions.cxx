#include <iostream>
#include <stdio.h>

#define MACRO_STR_NAME(arg) #arg
#define MACRO_STR_VALUE(arg) MACRO_STR_NAME(arg)
#define MACRO_STR_VALUE(arg) MACRO_STR_NAME(arg)

//#define MACRO_A
#define MACRO_B bvalue
#define MACRO_C


int main(){
  /*
   cd ~/misc/tests/cpp

   ~/misc/tests/cpp/definitions.cxx

   g++ definitions.cxx -DMACRO_A=avalue -std=c++11 && ./a.out
   g++ definitions.cxx "-DMACRO_D=MACRO_B" -std=c++11 && ./a.out

   */

  std::cout << "MACRO_STR_NAME(MACRO_A)  = " << MACRO_STR_NAME(MACRO_A) << std::endl;
  std::cout << "MACRO_STR_VALUE(MACRO_A) = " << MACRO_STR_VALUE(MACRO_A) << std::endl;

  std::cout << "MACRO_STR_NAME(MACRO_B)  = " << MACRO_STR_NAME(MACRO_B) << std::endl;
  std::cout << "MACRO_STR_VALUE(MACRO_B) = " << MACRO_STR_VALUE(MACRO_B) << std::endl;

  std::cout << "MACRO_STR_NAME(MACRO_C)  = " << MACRO_STR_NAME(MACRO_C) << std::endl;
  std::cout << "MACRO_STR_VALUE(MACRO_C) = " << MACRO_STR_VALUE(MACRO_C) << std::endl;

  std::cout << "MACRO_STR_NAME(MACRO_D)  = " << MACRO_STR_NAME(MACRO_D) << std::endl;
  std::cout << "MACRO_STR_VALUE(MACRO_D) = " << MACRO_STR_VALUE(MACRO_D) << std::endl;

  const char *str_a = MACRO_STR_VALUE(MACRO_A);
  std::cout << "str_a = " << str_a << std::endl;
  return 0;
}

