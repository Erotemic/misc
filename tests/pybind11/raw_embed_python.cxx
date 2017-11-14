#include <Python.h>

int main(int argc, char *argv[])
{
  /*

   gcc raw_embed_python.cxx `python -m pybind11 --includes` -L`python-config --configdir` `python-config --libs`  && ./a.out

   */
    Py_SetProgramName((wchar_t *)argv[0]);  /* optional but recommended */
    Py_Initialize();
    PyRun_SimpleString("from time import time,ctime\n"
        "print('Today is', ctime(time()))\n");
    Py_Finalize();
    return 0;
}
