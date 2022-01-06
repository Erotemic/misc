#!/bin/bash
__doc__="
Demo bash hash tables. Requries Bash >= 4

References:
    https://stackoverflow.com/questions/1494178/how-to-define-hash-tables-in-bash
"

declare -A MY_BASH_DICT=(
    ["0"]="1"
    ["key"]="value"
    ["arbitrary.key"]="arbitrary.value"
    ["weird.key.123"]="weird.value.123"
    ['arb3#!itrary.key.123']='arbitrary.value.123_3#!'  # Requires single quotes
    ["weird.key.#"]="weird.value.#"
    ["weird.key.@"]="weird.value.@"
    ["weird.key.!"]="weird.value.!"
    ["weird.key.#0"]="weird.value.#0"
    ["weird.key.@0"]="weird.value.@0"
    #["weird.key.!0"]="weird.value.!0"  # Doesn't work
    ['weird.key.!0']='weird.value.!0'  # DOES work if you use single quotes
    ['weird.key.()']='weird.value.)('  # DOES work if you use single quotes
)

printf "\n\n === SINGLE DICT LOOKUP === \n\n"
KEY="arbitrary.key"
VAL="${MY_BASH_DICT[${KEY}]}"
echo " * KEY='${KEY}', VAL='${VAL}'"

KEY='weird.key.!0'
VAL="${MY_BASH_DICT[${KEY}]}"
echo " * KEY='${KEY}', VAL='${VAL}'"

printf "\n\n === ITERATE BASH DICT ITEMS === \n\n"
for KEY in "${!MY_BASH_DICT[@]}"; do
    VAL="${MY_BASH_DICT[${KEY}]}"
    echo " * KEY='${KEY}', VAL='${VAL}'"
done
printf " === \n\n"
