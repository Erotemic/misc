#!/usr/bin/env bash
__doc__="
How to write a message that only a specific recipient (in this case Jon Crall) can read.

The steps are:

* Use my fingerprint to download my public key from a keyserver (which may need an update)

* Write your secret message as plain text

* Encrypt it with GPG such that only the recipient can read it

* Send the message (or broadcast it) to the recipient.
"

RECPIENT_FINGERPRINT=4AC8B478335ED6ED667715F3622BE571405441B4
grab_public_keys(){
    # https://keyserver.ubuntu.com/pks/lookup?search=4AC8B478335ED6ED667715F3622BE571405441B4&fingerprint=on&op=index
    # needs to be updated based on what servers are alive.
    # there should be an IPFS solution for this.
    #gpg --recv-keys --keyserver hkps://keyserver.ubuntu.com $RECPIENT_FINGERPRINT
    #gpg --recv-keys --keyserver hkps://keys.openpgp.org $RECPIENT_FINGERPRINT
    gpg --recv-keys --keyserver hkp://keyserver.ubuntu.com $RECPIENT_FINGERPRINT
    echo $RECPIENT_FINGERPRINT
}
grab_public_keys

# Write your secret message in plain text in a file.
YOUR_SECRET_TEXT_FPATH=path-to-your-PLAINTEXT-message.asc
echo "
--- START YOUR MESSAGE ---
Hello world,
This is a super secret message.
--- END YOUR MESSAGE ---
" > $YOUR_SECRET_TEXT_FPATH

# Now encrypt the plain text using my public gpg key (only I will be able
# to decrypt it)
YOUR_ENCRYPTED_FPATH=path-to-your-ENCRYPTED-message.asc
# Unless you have marked my public key as trusted  (i.e. you are sure that
# it came from me) you will be warned. You can say yes, unless you think
# this message might have been modified by a man in the middle.
rm -rf $YOUR_ENCRYPTED_FPATH
gpg --output $YOUR_ENCRYPTED_FPATH --encrypt --armor --recipient $RECPIENT_FINGERPRINT  $YOUR_SECRET_TEXT_FPATH

# Now send me this text
cat $YOUR_ENCRYPTED_FPATH


####
# Now on my end, I will decrypt


# Test that the recpiant can read it (this also should verify the sender)
# Its not possible to verify a message without decrypting it
MY_ENCRYPTED_FPATH=code.asc
MY_DECRYPT_FPATH=decrypted-message.txt

cat $YOUR_ENCRYPTED_FPATH > "$MY_ENCRYPTED_FPATH"
rm -rf "$MY_DECRYPT_FPATH"
gpg --decrypt --output "$MY_DECRYPT_FPATH" "$YOUR_ENCRYPTED_FPATH"
cat decrypted-message.txt





consise-version(){
    __doc__="
    For copy / pasting in chats
    "
    # For more info
    # https://github.com/Erotemic/misc/blob/d0c679b0ead85136613f22339a8aff1f93573269/learn/send_me_a_gpg_message.sh
    RECPIENT_FINGERPRINT=4AC8B478335ED6ED667715F3622BE571405441B4
    gpg --recv-keys --keyserver hkp://keyserver.ubuntu.com $RECPIENT_FINGERPRINT
    echo $RECPIENT_FINGERPRINT
    YOUR_SECRET_TEXT_FPATH=path-to-your-PLAINTEXT-message.asc
    echo "
    --- START YOUR MESSAGE ---
    Hello world,
    This is a super secret message.
    --- END YOUR MESSAGE ---
    " > $YOUR_SECRET_TEXT_FPATH
    YOUR_ENCRYPTED_FPATH=path-to-your-ENCRYPTED-message.asc
    rm -rf $YOUR_ENCRYPTED_FPATH
    gpg --output $YOUR_ENCRYPTED_FPATH --encrypt --armor --recipient $RECPIENT_FINGERPRINT  $YOUR_SECRET_TEXT_FPATH
    # Send me this message
    cat $YOUR_ENCRYPTED_FPATH
}
