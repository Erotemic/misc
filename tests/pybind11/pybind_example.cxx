#include <pybind11/pybind11.h>

namespace py = pybind11;

int add(int i, int j) {
    return i + j;
}

PYBIND11_MODULE(pybind_example, m) {
  /*

   c++ -O3 -Wall -shared -std=c++11 -fPIC `python -m pybind11 --includes` pybind_example.cxx -o pybind_example`python-config --extension-suffix`

   python -c "import pybind_example"
   python -c "import pybind_example; print(pybind_example.add(3, 4))"

   */
    m.doc() = "pybind_example plugin"; // optional module docstring

    m.def("add", &add, "A function which adds two numbers");

    py::exec(R"(
        kwargs = dict(name="World", number=42)
        message = "Hello, {name}! The answer is {number}".format(**kwargs)
        print(message)
    )");
}
