#!/bin/bash
# https://boubakr92.wordpress.com/2012/12/14/numeral-systems-conversion-in-bash/


toupper(){
    __doc__='
    printf "hi" | toupper 
    '
    awk '{ print toupper($0) }'
}

tolower(){
    __doc__='
    printf "fDDs" | tolower 
    '
    awk '{ print tolower($0) }'
}


### -- b64 inputs ###

b64_to_hex(){
    __doc__='
        echo "UUUU" | b64_to_hex
    '
    base64 -d | xxd -p | tr -d '\n'
}

b64_to_ascii(){
    __doc__='
        echo "UUUU" | b64_to_ascii
    '
    base64 -d
}

b64_to_oct(){
    __doc__='
        echo "UUUU" | b64_to_ascii
    '
    b64_to_hex | hex_to_oct
}

b64_to_b64(){
    cat
}


### -- ascii inputs ###

ascii_to_b64(){
    base64
}

ascii_to_hex(){
    __doc__='
    echo "Salted" | ascii_to_hex
    '
    xxd -p | tr -d '\n'
}

ascii_to_oct(){
    __doc__='
    echo "Salted" | ascii_to_oct
    echo "Salted" | ascii_to_hex
    echo "Salted" | ascii_to_b64 | b64_to_oct | oct_to_ascii
    '
    ascii_to_hex | hex_to_oct
}

sandwich_prefix_nl(){
    __doc__='
    printf "mes\nsa\nge" | sandwich "mypr\nefix"
    | cat
    '
    printf "%s" "$1"
    #echo -en "$@"
    cat - && 
    echo ""
}

ascii_to_ascii(){
    cat
}

### -- hex inputs ###

hex_to_oct(){
    __doc__='
    source ~/misc/learn/bash_base_conversions.sh
    echo 7 | hex_to_oct
    echo FF | hex_to_oct
    '
    toupper | sandwich_prefix_nl "obase=8 ; ibase=16 ; " \n | bc | tr -d '\n' | tr -d \\\\
}

hex_to_b64(){
    xxd -r -p | base64
}

hex_to_ascii(){
    __doc__='
    hex_to_ascii deadbeaf00000bad
    '
    xxd -r -p 
}

hex_to_hex(){
    cat
}


### -- oct inputs ###

oct_to_oct(){
    cat
}

oct_to_hex(){
    __doc__='
    source ~/misc/learn/bash_base_conversions.sh
    echo 15 | oct_to_hex 
    echo 37 | oct_to_hex 
    echo 1f | hex_to_oct 
    '
    sandwich_prefix_nl "obase=16 ; ibase=8 ; " | bc  | awk '{ print tolower($0) }' | tr -d '\n' | tr -d \\\\
}

oct_to_ascii() {
    __doc__='
    echo "46" | oct_to_hex 
    echo "26" | hex_to_ascii 
    echo "46" | oct_to_ascii 
    echo "&" |  ascii_to_hex 
    echo "&" | ascii_to_oct 
    '
    oct_to_hex | hex_to_ascii
}

oct_to_b64() {
    oct_to_ascii | ascii_to_b64
}


mwe(){
    #### TESTS
    SALT_PREFIX="Salted__"
    SALT_HEX="deadbeaf00000bad"
    printf "secret" | SECRET_PASSWORD=12345 openssl enc -aes-256-cbc -pbkdf2 -md sha512 -pass env:SECRET_PASSWORD -S "$SALT_HEX" -e -a 
    # OpenSSL 1.x output
    SALTED_CIPHERTEXT_B64_ORIG="U2FsdGVkX1/erb6vAAALrWJ5ujRXTt7kQoCwvQPCjJE="
    # OpenSSL 3.x output
    UNSALTED_CIPHERTEXT_B64="Ynm6NFdO3uRCgLC9A8KMkQ=="

    PART1_ACII="$SALT_PREFIX"
    PART2_HEX="$SALT_HEX"
    PART3_B64="$UNSALTED_CIPHERTEXT_B64"

    b64_to_ascii(){
        base64 -d
    }
    ascii_to_b64(){
        base64
    }
    hex_to_ascii(){
        xxd -r -p 
    }

    TMP_FPATH=$(mktemp)
    printf "" > "$TMP_FPATH"
    # shellcheck disable=SC2059
    printf "$PART1_ACII" > "$TMP_FPATH"
    # shellcheck disable=SC2059
    printf "$PART2_HEX" | hex_to_ascii >> "$TMP_FPATH"
    # shellcheck disable=SC2059
    printf "$PART3_B64" | b64_to_ascii >> "$TMP_FPATH"

    SALTED_CIPHERTEXT_B64_RECON=$(cat "$TMP_FPATH" | ascii_to_b64)

    if [[ "$SALTED_CIPHERTEXT_B64_RECON" == "$SALTED_CIPHERTEXT_B64_ORIG" ]]; then
        echo "correct reconstruction"
    else
        echo "incorrect reconstruction"
    fi

    (printf "Salted__" && printf "deadbeaf00000bad" | xxd -r -p && echo "$UNSALTED_CIPHERTEXT_B64" | base64 -d ) | base64
}

debug_scratch(){
    #### TESTS
    COMBO_ORIG_B64="U2FsdGVkX1/erb6vAAALrWJ5ujRXTt7kQoCwvQPCjJE="

    PART1_ACII="Salted__"
    PART2_HEX="deadbeaf00000bad"
    PART3_B64="Ynm6NFdO3uRCgLC9A8KMkQ=="

    # Tests
    TEST_B64="U2FsdGVkX1VV"
    TEST_ASCII="Salted_UU"
    TEST_HEX="53616c7465645f5555"
    TEST_OCT="246605543506254427652525"

    echo "--B64 conversions"
    echo -n "$TEST_B64" | b64_to_ascii && echo ""
    echo -n "$TEST_B64" | b64_to_b64 && echo ""
    echo -n "$TEST_B64" | b64_to_hex && echo "" 
    echo -n "$TEST_B64" | b64_to_oct && echo "" 

    echo "--ASCII conversions"
    echo -n "$TEST_ASCII" | ascii_to_ascii && echo ""
    echo -n "$TEST_ASCII" | ascii_to_b64 && echo ""
    echo -n "$TEST_ASCII" | ascii_to_hex && echo "" 
    echo -n "$TEST_ASCII" | ascii_to_oct && echo "" 

    echo "--HEX conversions"
    echo -n "$TEST_HEX" | hex_to_ascii && echo ""
    echo -n "$TEST_HEX" | hex_to_b64 && echo ""
    echo -n "$TEST_HEX" | hex_to_hex && echo "" 
    echo -n "$TEST_HEX" | hex_to_oct && echo "" 

    echo "--OCT conversions"
    echo "$TEST_OCT" | oct_to_ascii && echo ""
    echo "$TEST_OCT" | oct_to_b64 && echo ""
    echo "$TEST_OCT" | oct_to_hex && echo "" 
    echo "$TEST_OCT" | oct_to_oct && echo "" 

    echo "$COMBO_ORIG_B64" | b64_to_ascii && echo ""
    echo "$COMBO_ORIG_B64" | b64_to_hex && echo ""
    echo "$COMBO_ORIG_B64" | b64_to_oct && echo ""

    echo "$PART1_ACII" | ascii_to_hex
    echo "$PART1_ACII" | ascii_to_b64 | b64_to_oct

    echo "$PART1_ACII" | ascii_to_oct
    echo "$PART2_HEX" | hex_to_oct
    echo "$PART3_B64" | b64_to_oct

    echo "$PART1_ACII" | ascii_to_hex

    TMP_FPATH=$(mktemp)
    printf "" > "$TMP_FPATH"
    # shellcheck disable=SC2059
    printf "$PART1_ACII" | ascii_to_ascii > "$TMP_FPATH"
    # shellcheck disable=SC2059
    printf "$PART2_HEX" | hex_to_ascii >> "$TMP_FPATH"
    # shellcheck disable=SC2059
    printf "$PART3_B64" | b64_to_ascii >> "$TMP_FPATH"
    echo "24660554350625442765741215725557527400000056551423633506425647336710412005413640360506221" | oct_to_b64
}
