#!/usr/bin/env bash
__doc__='
References:
    https://stackoverflow.com/questions/9332802/how-to-write-a-bash-script-that-takes-optional-input-arguments
    https://www.codegrepper.com/code-examples/shell/shell+default+value+for+variable

CommandLine:
    bash ~/misc/tests/bash/bash_default_args.sh
'

demo_default_args(){
    FUNC_VAR1="${ARG_VAR1:-default1}"  # If variable not set or null, use default.
    FUNC_VAR2="${ARG_VAR2:=default2}"  # If variable not set or null, set it to default.
    : "${FUNC_VAR3:-default3}"  # Does this work?
    : "${FUNC_VAR4:=default4}"  # Does this work?
    FUNC_VAR5="${FUNC_VAR5:=default5}"  # Does this work?

    echo "FUNC_VAR1 = $FUNC_VAR1"
    echo "FUNC_VAR2 = $FUNC_VAR2"
    echo "FUNC_VAR3 = $FUNC_VAR3"
    echo "FUNC_VAR4 = $FUNC_VAR4"
    echo "FUNC_VAR5 = $FUNC_VAR5"
    echo "ARG_VAR1 = $ARG_VAR1"
    echo "ARG_VAR2 = $ARG_VAR2"
}

echo "=== CALL 1 ==="
demo_default_args
echo "===================="
echo "ARG_VAR1 = $ARG_VAR1"
echo "ARG_VAR2 = $ARG_VAR2"
echo "===================="

echo "=== CALL 2 ==="
ARG_VAR1="a" ARG_VAR2="b" demo_default_args
echo "===================="
echo "ARG_VAR1 = $ARG_VAR1"
echo "ARG_VAR2 = $ARG_VAR2"
echo "===================="


echo "=== CALL 3 ==="
FUNC_VAR3=value1 FUNC_VAR4=value2 FUNC_VAR5=value3 demo_default_args
echo "FUNC_VAR3 = $FUNC_VAR3"
echo "FUNC_VAR4 = $FUNC_VAR4"
echo "FUNC_VAR5 = $FUNC_VAR5"
echo "===================="


echo "=== CALL 4 ==="
demo_default_args
echo "FUNC_VAR3 = $FUNC_VAR3"
echo "FUNC_VAR4 = $FUNC_VAR4"
echo "FUNC_VAR5 = $FUNC_VAR5"
echo "===================="


#fob_list = []
#list_len = 0
#val = 1
#last = 0
#old = 0
#while list_len < length:
#    fob_list.append(val)
#    old = val
#    val += last
#    last = old
