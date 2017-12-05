#include <iostream>
#include <stdio.h>

#define NOOP(arg)
#define MACRO_STR_VALUE(arg) str0(arg) NOOP(MACRO_C)
#define str0(arg) #arg NOOP(MACRO_C)
//#define str1(arg) str2(arg)
//#define str2(arg)

//#define MACRO_A avalue

#define MACRO_A MACRO_B
#define MACRO_B MACRO_C
#define MACRO_C MACRO_D


int main(){
  /*
   //g++ mwe.cxx -DMACRO_B=_MACRO_A -std=c++11 && ./a.out
   g++ mwe.cxx -std=c++11 && ./a.out
   */

  std::cout << "MACRO_STR_VALUE(MACRO_A) = " << MACRO_STR_VALUE(MACRO_A) << std::endl;
  //std::cout << "MACRO_STR_VALUE(MACRO_B) = " << MACRO_STR_VALUE(MACRO_B) << std::endl;

  return 0;
}

