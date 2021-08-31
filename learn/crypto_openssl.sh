__doc__='
# List available ciphers
openssl ciphers | sed "s/:/\n/g"

'

# Setup the secret key and the secret message
SECRET_PASSWORD=AffiliateCarelessDepthGenreDeniableLandlordAutomatedAnguishedDeletion
PREFIX_MESSAGE="This is my super secret message.  If the prefix of this message does not match the hash at the end of this message, tampering were done."
PREFIX_SHA512=$(echo $PREFIX_MESSAGE | sha512sum)
SECRET_MESSAGE="$PREFIX_MESSAGE $PREFIX_SHA512"

PLAINTEXT_FILE_PATH=plaintext_secret.txt
ENCRYPTED_FILE_PATH=encrypted_secret.enc
DECRYPTED_FILE_PATH=decrypted_secret.txt

# Write the secret
# Encrypt the secret message
# Delete the message plaintext
echo $SECRET_MESSAGE > $PLAINTEXT_FILE_PATH
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
VALIDATED_SHA512=$(echo $DECRYPTED_MESSAGE | sha512sum)
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
TAMPERED_VALIDATED_SHA512=$(echo $TAMPERED_DECRYPTED_MESSAGE | sha512sum)
echo "TAMPERED_VALIDATED_SHA512 = $TAMPERED_VALIDATED_SHA512"
echo "EXPECTED_SHA512           = $PREFIX_SHA512"
