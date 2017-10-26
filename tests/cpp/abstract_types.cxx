#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include <mutex>

class Parent {
  public:
    Parent() : parent(2), foo(42) {

    }
    int parent;
    int foo;
};

class Child : public Parent {
  public:
    Child() : child(1) {

    }
    int child;
};


void func(Parent const& p){

  //std::cout << "p = " << p.foo << std::endl;
  //static_cast<Child>(p);
  //std::cout <<   << std::endl;

}

//void func(Child const& p){

//std::cout << "p = " << p.foo << std::endl;
//std::cout << "p = " << p.child << std::endl;

//}

int main(){
  /*
   g++ abstract_types.cxx -std=c++11 && ./a.out

   */
  std::shared_ptr<Child> self = std::make_shared<Child>();

  //std::cout << "self = " << self.get().child << std::endl;
  //std::cout << "self.parent = " << self.parent << std::endl;

  //func(self);

  return 0;
}
