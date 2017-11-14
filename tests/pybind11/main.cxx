#include <iostream>
#include <pybind11/embed.h>

namespace py = pybind11;

int main()
{
  /*

     python-config --libs

     python-config --configdir

     gcc main.cxx -Wall -fPIC -std=c++11 `python -m pybind11 --includes` -L`python-config --configdir` `python-config --libs` -lstdc++ && ./a.out

     # python2
     gcc main.cxx -Wall -fPIC -std=c++11 `python -m pybind11 --includes` -L/usr/lib/python2.7/config-x86_64-linux-gnu/ `python-config --libs` -lstdc++ && ./a.out


   */

  py::scoped_interpreter guard{};

  py::exec(R"(
        kwargs = dict(name="World", number=42)
        message = "Hello, {name}! The answer is {number}".format(**kwargs)
        print(message)
    )");

  py::object const mod = py::module::import("foo");
  mod.attr("bar")();

  py::module::import("foo").attr("bar")();

  return 1;
}
