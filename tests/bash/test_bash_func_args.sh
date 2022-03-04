#!/bin/bash
__doc__='

Takeaways:

1. Quoting an array when you pass it, maintains the same exact elements as the
   inputs. So it is correct to do:

   Doing:
       `subfunction "$@"`
   Will maintain the length of the array and keep items bundled correctly.

   And doing 
       `subfunction $@`
   May break items appart and increase the number of items in the array.
'


bash_parameter_test(){
    # https://linuxize.com/post/bash-functions/#passing-arguments-to-bash-functions
    echo "#args = \$# = $#"
    echo " args = \$@ = $@"
    echo "\$1 = $1"
    echo "\$2 = $2"
    echo "\$3 = $3"

    # Convert to an array (this does handle the weird case correctly, which is
    # what we want to verify with this script )
    ARGS=("$@")
    echo "    ARGS  = ${ARGS[@]}"
    # Print args in a way that always expands quotes
    # https://stackoverflow.com/a/12985353
    echo "    ARGS  = ($(printf "\"%s\" " "${ARGS[@]}"))"
    echo "len(ARGS) = ${#ARGS}"
}

bash_parameter_test
bash_parameter_test "one"
bash_parameter_test "one" "two" "three"

# This is the interesting case because the arg $2 has a space
bash_parameter_test "one" "two five" "three"

# Show how to expand an array and pass it to a function
ARRAY=("one" "a b c " "d" "e f g")
bash_parameter_test "${ARRAY[@]}"


bash_array_repr(){
    __doc__='
    Given a bash array, this should print a literal copy-pastable
    representation

    Example:
        ARR=(1 "2 3" 4)
        bash_array_repr "${ARR[@]}"

    '
    ARGS=("$@")
    if [ "${#ARGS}" -gt 0 ]; then
        # Not sure if the double or single quotes is better here
        echo "($(printf "'%s' " "${ARGS[@]}"))"
        #echo "($(printf "\'%s\' " "${ARGS[@]}"))"
    else
        echo "()"
    fi
}

ARR=(1 "2 3" 4)
bash_array_repr "${ARR[@]}"

# To use within another echo, need to do something junky like this
_REPR=$(bash_array_repr "${ARR[@]}")
echo "ARR = $_REPR"

ARR=()
bash_array_repr "${ARR[@]}"
_REPR=$(bash_array_repr "${ARR[@]}")
echo "ARR = $_REPR"


escape_bash_string(){
    __doc__='
    Escapes the input string so the program that it is passed to sees exactly
    the given input string.

    TODO:
        - [ ] Add to erotemic.utils

    Args:
        The string to escape

    Returns:
        The escaped string

    Example:
        escape_bash_string "one-word" && echo ""
        escape_bash_string "two words" && echo ""
        escape_bash_string "\"a quoted phrase\"" && echo ""
        escape_bash_string "\"a literal \" quoted phrase\"" && echo ""
        escape_bash_string "oh \" no \" so \" my \" ba \" \"\" \\ hm" && echo ""
        escape_bash_string "backslashes \\\\\\\\" && echo ""
        escape_bash_string "three words" && echo ""
        escape_bash_string "path\"o\"log ic" && echo ""
    '
    printf "%q" "$1"
}


_print_call_sig(){
    printf "_print_call_sig"
    ARGS=("$@")
    for ARG in "${ARGS[@]}"; do
        ESCAPED_ARG=$(escape_bash_string "$ARG")
        printf " %s" "$ESCAPED_ARG"
    done
    printf "\n"
}


demo_array_use_cases(){
    __doc__='
    Demo different array use cases

    References:
        .. [1] https://opensource.com/article/18/5/you-dont-know-bash-intro-bash-arrays

    Table from [1]:

        arr=()	        Create an empty array
        arr=(1 2 3)	    Initialize array
        ${arr[2]}	    Retrieve third element
        ${arr[@]}	    Retrieve all elements
        ${!arr[@]}	    Retrieve array indices
        ${#arr[@]}	    Calculate array size
        arr[0]=3	    Overwrite 1st element
        arr+=(4)	    Append value(s)
        str=$(ls)	    Save ls output as a string
        arr=( $(ls) )	Save ls output as an array of files
        ${arr[@]:s:n}	Retrieve n elements starting at index s
    '

    # Concept:
    #     * All args to a bash function are available in the special @ array.

    # 
    # Copy all function args into a bash array
    # We will show how to work with any array variable $ARR
    ARR=("$@")


    # Print via ARR and via @
    echo " ==== DEMO ARRAY USE CASES ===="
    echo "PRINT TEST"
    echo "ARR = "$(bash_array_repr "${ARR[@]}")
    echo "@   = "$(bash_array_repr "${@}")

    # Get the length of an array
    echo ""
    echo "LENGTH TEST"
    echo "len(ARR) = ${#ARR[@]}"
    echo "len(@)   = ${#}"

    # Pass array to another function as all args (similar to *args in Python)
    printf "\nCALLSIG TEST\n"
    _print_call_sig "${@}"
    _print_call_sig "${ARR[@]}"

    # Loop over array
    echo ""
    echo "LOOP TEST"
    echo "Loop ARR"
    for ARG in "${ARR[@]}"; do
        echo "  * ARG = $ARG"
    done
    echo "Loop @"
    for ARG in "${@}"; do
        echo "  * ARG = $ARG"
    done
    echo " ==== END DEMO ARRAY USE CASES ===="
}

INPUT_ARR=(1 "2 3" 4 "five" "bobby tables" "path'o'lo\"ic")
demo_array_use_cases "${INPUT_ARR[@]}"




# Example of THE RIGHT WAY™ to pass array arguments around in bash funcs

check_handler(){
    # tests the _handle_help ars really should be quoted
    for var in "$@"
    do
        echo "var=$var"
    done
    return 0
}

func_stack3(){
    # Either of these works

    #ARGS=("$@")
    #bash_array_repr "${ARGS[@]}"

    bash_array_repr "$@"
}

func_stack2(){
    #func_stack3 $@
    #func_stack3 "$@"
    func_stack3 "${@}"
}

func_stack1(){
    #func_stack2 $@
    #func_stack2 "$@"

    #check_handler $@  # incorrect

    # This is THE RIGHT WAY™
    check_handler "$@"
    func_stack2 "${@}"
}

func_stack1 1 2 "3 4 5"



positional_arg_test(){
    # How to define default arguments
    # Positional only
    ARG1=$1
    # Defaulted positional only
    ARG2=${2:-"Arg2-Default"}
    ARG3=${2:-"Arg3-Default"}
    # Defaulted positional+keyword
    ARG4=${ARG4:-${4:-"Arg4-Default"}}
    ARG5=${ARG5:-${5:-"Arg5-Default"}}
    # Keywords only
    KWARG_1=${KWARG_1:-"KEYWORD_ARG1-DEFAULT"}
    KWARG_2=${KWARG_2:-"KEYWORD_ARG2-DEFAULT"}
    echo "
    ARG1 = $ARG1
    ARG2 = $ARG2
    ARG3 = $ARG3
    ARG4 = $ARG4
    KWARG_1 = $KWARG_1
    KWARG_2 = $KWARG_2
    "
}


positional_arg_test
ARG4="arg4-specified" KWARG_2="kwarg2-specified" positional_arg_test "arg1-specified" "arg2-specified" "arg3-specified" 
ARG4="arg4-specified" KWARG_2="kwarg2-specified" positional_arg_test 
ARG5="arg2-specified" KWARG_2="kwarg2-specified" positional_arg_test 

ARG4="arg4-specified" positional_arg_test a b c d e f g

all_keyword_func(){
    KEY1=${1:-${KEY1:-"None"}}
    KEY2=${2:-${KEY2:-"None"}}
    KEY3=${3:-${KEY3:-"None"}}
}


