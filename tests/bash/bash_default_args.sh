#!/bin/bash
# https://stackoverflow.com/questions/9332802/how-to-write-a-bash-script-that-takes-optional-input-arguments
# https://www.codegrepper.com/code-examples/shell/shell+default+value+for+variable

demo_default_args(){
    FUNC_VAR1="${ARG_VAR1:-default1}"  # If variable not set or null, use default.
    FUNC_VAR2="${ARG_VAR2:=default2}"  # If variable not set or null, set it to default.
    echo "FUNC_VAR1 = $FUNC_VAR1"
    echo "FUNC_VAR2 = $FUNC_VAR2"
    echo "ARG_VAR1 = $ARG_VAR1"
    echo "ARG_VAR2 = $ARG_VAR2"
}

demo_default_args
echo "===================="
echo "ARG_VAR1 = $ARG_VAR1"
echo "ARG_VAR2 = $ARG_VAR2"
echo "===================="

ARG_VAR1="a" ARG_VAR2="b" demo_default_args
echo "===================="
echo "ARG_VAR1 = $ARG_VAR1"
echo "ARG_VAR2 = $ARG_VAR2"
echo "===================="


fob_list = []
list_len = 0
val = 1
last = 0
old = 0
while list_len < length:
    fob_list.append(val)
    old = val
    val += last
    last = old
