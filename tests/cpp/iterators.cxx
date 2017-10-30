#include <iostream>
#include <vector>
#include <memory>


typedef std::vector< int > int_set;
typedef std::shared_ptr< int_set > int_set_sptr;

int_set_sptr testdata_intset()
{
  int_set_sptr items_sptr = std::make_shared<int_set>();
  for (int i = 0; i < 10; ++i)
  {
    items_sptr->push_back(1 << i);
  }
  return items_sptr;
}

int main(){
  //R"__doc__(
  //CommandLine:
  //  g++ iterators.cxx -std=c++11 && ./a.out
  //)__doc__";

  int_set_sptr items_sptr = testdata_intset();

  std::cout << "items_sptr = " << items_sptr << std::endl;
  //std::cout << "items_sptr->begin() = " << items_sptr->begin() << std::endl;

  //for(int j = 0; j < 10; ++j)
  //{
  //  auto item = items_sptr->at(j);
  //  std::cout << "item = " << item << std::endl;
  //}

  //int_set items = (*items_sptr.get());

  //for(int j = 0; j < 10; ++j)
  //{
  //  auto item = items[j];
  //  std::cout << "item = " << item << std::endl;
  //}

  for(auto item : *items_sptr.get())
  {
    std::cout << "item = " << item << std::endl;
  }

  //std::cout << "self = " << self.get().child << std::endl;
  //std::cout << "self.parent = " << self.parent << std::endl;

  //func(self);

  return 0;
}

