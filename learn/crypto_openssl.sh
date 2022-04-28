#!/bin/bash
__doc__='
# List available ciphers
openssl ciphers | sed "s/:/\n/g"
'

# OpenSSL Standalone stdin demo:
echo "secret_text" | SECRET_PASSWORD=12345 openssl enc -aes-256-cbc -pbkdf2 -md sha512 -pass env:SECRET_PASSWORD -S "deadbeaf00000bad" -e -a 
echo "U2FsdGVkX1/erb6vAAALrdMUExJTaVfj5d60EGl8Gu0=" | SECRET_PASSWORD=12345 openssl enc -aes-256-cbc -pbkdf2 -md sha512 -pass env:SECRET_PASSWORD -d -a 


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
