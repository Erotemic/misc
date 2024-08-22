#!/usr/bin/env bash
__doc__='
Notes on bash array syntax

References:
    .. [1] https://opensource.com/article/18/5/you-dont-know-bash-intro-bash-arrays
    .. [2] https://stackoverflow.com/a/18887210/887074

See Also:
    ~/misc/tests/bash/test_bash_func_args.sh
'
source "$HOME/local/init/utils.sh"

# Initialize array
arr1=(1 2 3 9 3 2 8 9)

# Empty array
arr2=()

# Loop over an array
for item in "${arr1[@]}"; do
    echo "  * item = $item"
    # Append to an array
    arr2+=("$item")
done

# Sort array
readarray -t sorted_arr < <(printf '%s\n' "${arr2[@]}" | sort)

bash_array_repr "${sorted_arr[@]}"


# Length of an array
length=${#sorted_arr[@]}
echo "length = $length"


#ARRAY=("one" "a b c " "d" "e f g")
#arr=()	        Create an empty array
#arr=(1 2 3)	    Initialize array
#${arr[2]}	    Retrieve third element
#${arr[@]}	    Retrieve all elements
#${!arr[@]}	    Retrieve array indices
#${#arr[@]}	    Calculate array size
#arr[0]=3	    Overwrite 1st element
#arr+=(4)	    Append value(s)
#str=$(ls)	    Save ls output as a string
#arr=( $(ls) )	Save ls output as an array of files  # WRONG
#${arr[@]:s:n}	Retrieve n elements starting at index s


declare -a arr_10=()
arr_10+=('a' 'b' '3'  '4 5 32')
bash_array_repr "${arr_10[@]}"

# Copy an array into a dynamically named variable
ARRAY_NAME="arr_12"
readarray -t "$ARRAY_NAME" < <(printf '%s\n' "${arr_10[@]}")
# shellcheck disable=SC2154
bash_array_repr "${arr_12[@]}"


ls_array(){
    __doc__='
    Read the results of a glob pattern into an array

    See Also: ~/local/init/utils.sh

    Args:
        arr_name
        glob_pattern

    Example:
        arr_name="myarray"
        glob_pattern="*"
        pass
        bash_array_repr "${array[@]}"
        mkdir -p $HOME/tmp/tests/test_ls_arr
        cd $HOME/tmp/tests/test_ls_arr
        touch "$HOME/tmp/tests/test_ls_arr/path ological files"
        touch "$HOME/tmp/tests/test_ls_arr/are so fun"
        touch "$HOME/tmp/tests/test_ls_arr/foo"
        touch "$HOME/tmp/tests/test_ls_arr/bar"
        touch "$HOME/tmp/tests/test_ls_arr/baz"
        touch "$HOME/tmp/tests/test_ls_arr/biz"
        touch "$HOME/tmp/tests/test_ls_arr/fake_newline\n in fils? YES!"
        python -c "import ubelt; ubelt.Path(\"$HOME/tmp/tests/test_ls_arr/Real newline \n in fname\").expand().touch()"
        python -c "import ubelt; ubelt.Path(\"$HOME/tmp/tests/test_ls_arr/Realnewline\ninfname\").expand().touch()"

        arr_name="myarray"
        glob_pattern="*"
        ls_array "$arr_name" "$glob_pattern"
        bash_array_repr "${array[@]}"
    '
    local arr_name="$1"
    local glob_pattern="$2"
    shopt -s nullglob
    # shellcheck disable=SC2206
    array=($glob_pattern)
    shopt -u nullglob # Turn off nullglob to make sure it doesn't interfere with anything later
    # Copy the array into the dynamically named variable
    readarray -t "$arr_name" < <(printf '%s\n' "${array[@]}")
}


# https://www.tutorialkart.com/bash-shell-scripting/bash-append-an-array-to-another-array/
##  Extend array
arr1=("apple" "banana" "cherry")
arr2=("mango" "grape")
arr1+=("${arr2[@]}")
bash_array_repr "${arr1[@]}"

arr1=("apple" "banana" "cherry")
arr2=()
arr1+=("${arr2[@]}")
bash_array_repr "${arr1[@]}"

arr1=()
arr2=()
arr1+=("${arr2[@]}")
bash_array_repr "${arr1[@]}"

arr1=('dist/pyhesaff-2.1.0.tar.gz' )
arr2=()
arr1+=("${arr2[@]}")
bash_array_repr "${arr1[@]}"
