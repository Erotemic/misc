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
