#!/bin/bash
__doc__='
# List available ciphers
openssl ciphers | sed "s/:/\n/g"
'

# OpenSSL Standalone stdin demo:
printf "secret" | SECRET_PASSWORD=12345 openssl enc -aes-256-cbc -pbkdf2 -md sha512 -pass env:SECRET_PASSWORD -S "deadbeaf00000bad" -e -a 
echo "U2FsdGVkX1/erb6vAAALrWJ5ujRXTt7kQoCwvQPCjJE=" | SECRET_PASSWORD=12345 openssl enc -aes-256-cbc -pbkdf2 -md sha512 -pass env:SECRET_PASSWORD -d -a && echo ""

# OpenSSL3
printf "secret" | SECRET_PASSWORD=12345 openssl enc -aes-256-cbc -pbkdf2 -md sha512 -pass env:SECRET_PASSWORD -S "deadbeaf00000bad" -e 

echo "Ynm6NFdO3uRCgLC9A8KMkQ==" | SECRET_PASSWORD=12345 openssl enc -aes-256-cbc -pbkdf2 -S "deadbeaf00000bad" -md sha512 -pass env:SECRET_PASSWORD -d -a && echo "--"


# https://boubakr92.wordpress.com/2012/12/14/numeral-systems-conversion-in-bash/

toupper(){
    __doc__="
    toupper asdf
    "
    printf '%s\n' "$1" | awk '{ print toupper($0) }'
}

tolower(){
    __doc__="
    tolower FDS
    "
    printf '%s\n' "$1" | awk '{ print tolower($0) }'
}

convert_b64_to_hex(){
    echo "$1" | base64 -d | xxd -p -u
}

convert_b64_to_ascii(){
    echo "$1" | base64 -d
}

convert_b64_to_oct(){
    local _hex
    _hex=$(convert_b64_to_hex "$1")
    convert_hex_to_oct "$_hex"
}

convert_ascii_to_b64(){
    echo "$1" | base64
}

convert_ascii_to_hex(){
    printf "%s" "$1" | xxd -p -u
}

convert_ascii_to_oct(){
    local _hex
    _hex=$(convert_ascii_to_hex "$1")
    convert_hex_to_oct "$_hex"
}

convert_hex_to_oct(){
    __doc__="
    convert_hex_to_oct 7
    convert_hex_to_oct FF
    "
    local _hex
    _hex=$(toupper "$1")
    echo "obase=8 ; ibase=16 ; $_hex" | bc
}

convert_hex_to_b64(){
    echo "$1" | xxd -r -p | base64
}

convert_hex_to_ascii(){
    echo "$1" | xxd -r -p 
}

convert_oct_to_hex(){
    __doc__='
    convert_oct_to_hex 15
    convert_oct_to_hex 37
    convert_hex_to_oct 1f
    '
    echo "obase=16 ; ibase=8 ; $1" | bc | awk '{ print tolower($0) }'
}

convert_oct_to_ascii() {
    __doc__='
    convert_oct_to_hex 46
    convert_hex_to_ascii 26
    convert_oct_to_ascii 46
    convert_ascii_to_hex "&"
    convert_ascii_to_oct "&"
    '
    local _hex
    _hex=$(convert_oct_to_hex "$1")
    convert_hex_to_ascii "$_hex"
}

convert_oct_to_b64() {
    local _ascii
    _ascii=$(convert_oct_to_ascii "$1")
    convert_ascii_to_b64 "$_ascii"
}

# Tests
TEST_B64="U2FsdGVkX1VV"
TEST_ASCII="Salted_UU"
TEST_HEX="53616C7465645F5555"

echo "$TEST_ASCII" | hd

convert_b64_to_oct "$TEST_B64" && true
convert_b64_to_hex "$TEST_B64" && true
convert_b64_to_ascii "$TEST_B64" && echo ""
convert_ascii_to_b64 "$TEST_ASCII" && true

convert_hex_to_b64 53616C7465645F5555
convert_hex_to_oct 53616C7465645F5555
convert_hex_to_b64 53616C7465645F5555
convert_hex_to_ascii 53616C7465645F5555

convert_oct_to_ascii "246605543506254427652525"
convert_oct_to_b64 "246605543506254427652525"

concat2(){
    printf "%s%s" "$1" "$2"
}

echo "obase=64; ibase=8; AAAA" | bc


# OpenSSL 1.x output
SALTED_CIPHERTEXT_B64_ORIG="U2FsdGVkX1/erb6vAAALrWJ5ujRXTt7kQoCwvQPCjJE="
# OpenSSL 3.x output
UNSALTED_CIPHERTEXT_B64="Ynm6NFdO3uRCgLC9A8KMkQ=="

echo "$SALTED_CIPHERTEXT_B64_ORIG" | hd -o
echo "$UNSALTED_CIPHERTEXT_B64" | od

# The prefix and salt 
SALT_PREFIX_ASCII="Salted__"
SALT_VALUE_HEX="DEADBEAF00000BAD"

echo $SALT_PREFIX_ASCII | od -r



# Conversions (via OCT)
UNSALTED_CIPHERTEXT_OCT=$(convert_b64_to_oct "$UNSALTED_CIPHERTEXT_B64")
SALT_PREFIX_OCT=$(convert_ascii_to_oct "$SALT_PREFIX_ASCII")
SALT_VALUE_OCT=$(convert_hex_to_oct "$SALT_VALUE_HEX")
SALT_HEADER_OCT=$(concat2 "$SALT_PREFIX_OCT" "$SALT_VALUE_OCT")
SALTED_CIPHERTEXT_OCT=$(concat2 "$SALT_HEADER_OCT" "$UNSALTED_CIPHERTEXT_OCT")
SALTED_CIPHERTEXT_B64_RECON=$(convert_oct_to_b64 "$SALTED_CIPHERTEXT_OCT")
echo "SALTED_CIPHERTEXT_B64_ORIG  = $SALTED_CIPHERTEXT_B64_ORIG"
echo "SALTED_CIPHERTEXT_B64_RECON = $SALTED_CIPHERTEXT_B64_RECON"


# Conversions (via ASCII)
UNSALTED_CIPHERTEXT_ASCII=$(convert_b64_to_ascii "$UNSALTED_CIPHERTEXT_B64")
SALT_VALUE_ASCII=$(convert_hex_to_ascii $SALT_VALUE_HEX)
SALT_HEADER_ASCII=$(concat2 "$SALT_PREFIX_ASCII" "$SALT_VALUE_ASCII")
SALTED_CIPHERTEXT_ASCII=$(concat2 "$SALT_HEADER_ASCII" "$UNSALTED_CIPHERTEXT_ASCII")
SALTED_CIPHERTEXT_B64_RECON=$(convert_ascii_to_b64 "$SALTED_CIPHERTEXT_ASCII")
echo "SALTED_CIPHERTEXT_B64_ORIG  = $SALTED_CIPHERTEXT_B64_ORIG"
echo "SALTED_CIPHERTEXT_B64_RECON = $SALTED_CIPHERTEXT_B64_RECON"

# --- Conversions ---
#SALT_PREFIX_B64=$(convert_ascii_to_b64 "$SALT_PREFIX_ASCII")
#SALT_PREFIX_HEX=$(convert_ascii_to_hex "$SALT_PREFIX_ASCII")
##SALT_VALUE_HEX=$SALT_VALUE_HEX
#SALT_HEADER_HEX=$(concat2 "$SALT_PREFIX_HEX" "$SALT_VALUE_HEX")

#SALT_PREFIX_OCT=$(convert_hex_to_oct "$SALT_PREFIX_HEX")
#SALT_VALUE_OCT=$(convert_hex_to_oct "$SALT_VALUE_HEX")
#SALT_HEADER_OCT=$(concat2 "$SALT_PREFIX_OCT" "$SALT_VALUE_OCT")


# Base64 depends on multiples of 3, 4, and 16
# https://stackoverflow.com/questions/4080988/why-does-base64-encoding-require-padding-if-the-input-length-is-not-divisible-by
# In the base64 encoding, there are 65 possible symbols
# A-Z, a-z, 0-9, + and / represent 0-63, and = is the pad character which does not influence the actual encoding
# Each symbol represents a group of 6 bits.
# Groups of 24 bits are 3 characters
#-----------------------------------

# 
printf AAAA | base64 -d | hd
printf Salted__ | base64 | hd
printf UUU | base64 

printf U2Fs | base64 -d
#| hd

# Configurable Sandalone OpenSSL Demo
password="12345"
kdf_options="-pbkdf2 -iter 1000"
cipher=aes-256-cbc
md_digest="sha256"
salt=deadbeaf00000bad

read -ra kdf_option_array <<<"${kdf_options}"
echo "secret_text" | SECRET_PASSWORD=${password} openssl enc -"${cipher}" -md "${md_digest}" "${kdf_option_array[@]}" -pass env:SECRET_PASSWORD -S "${salt}" -e -a 
echo "U2FsdGVkX1/erb6vAAALrcaDZJ0Ixb0qwGA4VBjTQS4=" | SECRET_PASSWORD=${password} openssl enc -"${cipher}" -md "${md_digest}" "${kdf_option_array[@]}" -pass env:SECRET_PASSWORD -d -a 



# Bigger Demo

# Setup the secret key and the secret message
SECRET_PASSWORD=AffiliateCarelessDepthGenreDeniableLandlordAutomatedAnguishedDeletion
PREFIX_MESSAGE="This is my super secret message.  If the prefix of this message does not match the hash at the end of this message, tampering were done."
PREFIX_SHA512=$(echo "$PREFIX_MESSAGE" | sha512sum)
SECRET_MESSAGE="$PREFIX_MESSAGE $PREFIX_SHA512"

PLAINTEXT_FILE_PATH=plaintext_secret.txt
ENCRYPTED_FILE_PATH=encrypted_secret.enc
DECRYPTED_FILE_PATH=decrypted_secret.txt

# Write the secret
# Encrypt the secret message
# Delete the message plaintext
echo "$SECRET_MESSAGE" > $PLAINTEXT_FILE_PATH
SECRET_PASSWORD=$SECRET_PASSWORD openssl enc -aes-256-cbc -pbkdf2 -md SHA512 -pass env:SECRET_PASSWORD -e -a -in $PLAINTEXT_FILE_PATH > $ENCRYPTED_FILE_PATH
rm $PLAINTEXT_FILE_PATH

echo ""
echo "Contents of ENCRYPTED_FILE_PATH=$ENCRYPTED_FILE_PATH"
cat $ENCRYPTED_FILE_PATH 

# Decrypt the untampered secret
SECRET_PASSWORD=$SECRET_PASSWORD openssl enc -aes-256-cbc -pbkdf2 -md SHA512 -pass env:SECRET_PASSWORD -d -a -in $ENCRYPTED_FILE_PATH > $DECRYPTED_FILE_PATH
echo ""
echo "Contents of DECRYPTED_FILE_PATH=$DECRYPTED_FILE_PATH"
cat $DECRYPTED_FILE_PATH

# Show how we can validate the hash
DECRYPTED_MESSAGE=$(python -c "print(open('$DECRYPTED_FILE_PATH').read()[:-132])")
VALIDATED_SHA512=$(echo "$DECRYPTED_MESSAGE" | sha512sum)
echo "VALIDATED_SHA512 = $VALIDATED_SHA512"
echo "EXPECTED_SHA512  = $PREFIX_SHA512"


# Tamper with the file. Change one character 
TAMPERED_ENCRYPTED_FILE_PATH=tampered.enc
TAMPERED_DECRYPTED_FILE_PATH=tampered.txt
sed 's/^\(.\{40\}\)./\1Z/g' $ENCRYPTED_FILE_PATH > $TAMPERED_ENCRYPTED_FILE_PATH


# Decrypt the untampered secret
SECRET_PASSWORD=$SECRET_PASSWORD openssl enc -aes-256-cbc -pbkdf2 -md SHA512 -pass env:SECRET_PASSWORD -d -a -in $TAMPERED_ENCRYPTED_FILE_PATH > $TAMPERED_DECRYPTED_FILE_PATH
echo ""
echo "Contents of TAMPERED_DECRYPTED_FILE_PATH=$TAMPERED_DECRYPTED_FILE_PATH"
cat $TAMPERED_DECRYPTED_FILE_PATH

# Detect that the file was tampered with. 
# the hash will be different.
TAMPERED_DECRYPTED_MESSAGE=$(python -c "print(open('$TAMPERED_DECRYPTED_FILE_PATH').read()[:-132])")
TAMPERED_VALIDATED_SHA512=$(echo "$TAMPERED_DECRYPTED_MESSAGE" | sha512sum)
echo "TAMPERED_VALIDATED_SHA512 = $TAMPERED_VALIDATED_SHA512"
echo "EXPECTED_SHA512           = $PREFIX_SHA512"


# Test the pbkdf2 
sudo apt install nettle-bin


# https://github.com/elasticdog/transcrypt/issues/55
nettle-pbkdf2

# NOTE: salt must be 16 bytes, its openssl standard

encrypted_filename=encrypted_secret.txt
filename=plaintext_secret.txt
echo "super duper secret" > $filename

password=12345
cipher=aes-256-cbc

# Encrypt with salt
salt=$(openssl dgst -hmac "${filename}:${password}" -sha512 "$filename" | tr -d '\r\n' | tail -c 16)
ENC_PASS=$password openssl enc -$cipher -md SHA512 -pass env:ENC_PASS -pbkdf2 -e -a -S "$salt" -in "$filename" > "$encrypted_filename"
cat "$encrypted_filename"

# Demo how the salt is part of the file
printf "%s" "$salt" | hd
cat $encrypted_filename | base64 -d | hd


# (Try to recreate the encryption with a manual salt instead of -S)
salt=$(openssl dgst -hmac "${filename}:${password}" -sha512 "$filename" | tr -d '\r\n' | tail -c 16)

ENC_PASS=$password openssl enc -$cipher -md SHA512 -pass env:ENC_PASS -pbkdf2 -e -a -S "$salt" -in "$filename" -P
printf "%s" "$password" | nettle-pbkdf2 "$salt" --raw | hd

# Try to recreate
ENC_PASS="$DERIVED_PASS" openssl enc -$cipher -md SHA512 -pass env:ENC_PASS -pbkdf2 -e -a -nosalt -in "$filename" | base64 -d | hd

# Compare to regular
ENC_PASS=$password openssl enc -$cipher -md SHA512 -pass env:ENC_PASS -pbkdf2 -e -a -S "$salt" -in "$filename" | base64 -d | hd

# Decrypt
ENC_PASS=$password openssl enc -$cipher -md SHA512 -pass env:ENC_PASS -pbkdf2 -d -a -in "$encrypted_filename"


# Encrypt with salt
sudo apt install nettle-bin
echo "$password" | nettle-pbkdf2 "$salt"


filename=plaintext_secret.txt
password=12345
echo "super secret" > $filename
salt=$(openssl dgst -mac "${filename}:${password}" -sha512 "$filename" | tr -d '\r\n' | tail -c 16)
echo "salt = $salt"
echo "super duper secret" > $filename
salt=$(openssl dgst -hmac "${filename}:${password}" -sha512 "$filename" | tr -d '\r\n' | tail -c 16)
echo "salt = $salt"


### The code for openssl encode is here: https://github.com/openssl/openssl/blob/OpenSSL_1_1_1/apps/enc.c
### raw password originally stored in "pass" variable
### Moved into "str" variable 
### if pbkdf2 is enabled it uses PKCS5_PBKDF2_HMAC to generate "key" and "iv"
### if pbkdf2 is disabled it uses EVP_BytesToKey to generate "key" and "iv"

### The code for pbkdf2 is here: https://github.com/openssl/openssl/blob/5f1424c6bdca8ddb9d5d88a78a1d738be19c4ea8/crypto/evp/p5_crpt2.c
