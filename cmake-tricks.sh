make_cmake_graph(){
    # https://stackoverflow.com/questions/30793804/how-do-i-list-the-defined-make-targets-from-the-command-line
    cmake --graphviz=test.graph .
    dotty test.graph
}
