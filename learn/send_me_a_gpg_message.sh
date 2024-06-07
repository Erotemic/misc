#!/usr/bin/env bash
__doc__="
How to write a message that only a specific recipient (in this case Jon Crall) can read.

The steps are:

* Use my fingerprint to download my public key from a keyserver (which may need an update)

* Write your secret message as plain text

* Encrypt it with GPG such that only the recipient can read it

* Send the message (or broadcast it) to the recipient.
"

RECIPIENT_FINGERPRINT=4AC8B478335ED6ED667715F3622BE571405441B4
grab_public_keys(){
    # https://keyserver.ubuntu.com/pks/lookup?search=4AC8B478335ED6ED667715F3622BE571405441B4&fingerprint=on&op=index
    # needs to be updated based on what servers are alive.
    # there should be an IPFS solution for this.
    #gpg --recv-keys --keyserver hkps://keyserver.ubuntu.com $RECIPIENT_FINGERPRINT
    #gpg --recv-keys --keyserver hkps://keys.openpgp.org $RECIPIENT_FINGERPRINT
    gpg --recv-keys --keyserver hkp://keyserver.ubuntu.com $RECIPIENT_FINGERPRINT
    echo $RECIPIENT_FINGERPRINT
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
gpg --output $YOUR_ENCRYPTED_FPATH --encrypt --armor --recipient $RECIPIENT_FINGERPRINT  $YOUR_SECRET_TEXT_FPATH

# Now send me this text
cat $YOUR_ENCRYPTED_FPATH


####
# Now on my end, I will decrypt


# Test that the recipient can read it (this also should verify the sender)
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
    RECIPIENT_FINGERPRINT=4AC8B478335ED6ED667715F3622BE571405441B4
    gpg --recv-keys --keyserver hkp://keyserver.ubuntu.com $RECIPIENT_FINGERPRINT
    echo $RECIPIENT_FINGERPRINT
    YOUR_SECRET_TEXT_FPATH=path-to-your-PLAINTEXT-message.asc
    echo "
    --- START YOUR MESSAGE ---
    Hello world,
    This is a super secret message.
    --- END YOUR MESSAGE ---
    " > $YOUR_SECRET_TEXT_FPATH
    YOUR_ENCRYPTED_FPATH=path-to-your-ENCRYPTED-message.asc
    rm -rf $YOUR_ENCRYPTED_FPATH
    gpg --output $YOUR_ENCRYPTED_FPATH --encrypt --armor --recipient $RECIPIENT_FINGERPRINT  $YOUR_SECRET_TEXT_FPATH
    # Send me this message
    cat $YOUR_ENCRYPTED_FPATH
}


# Functional variants that do not use intermediate files:

send-gpg-message(){
    __doc__='
    Encrypts a message and prints cyphertext to screen.
    Send or broadcast the message such that the recipient gets it.
    '
    RECIPIENT_FINGERPRINT=4AC8B478335ED6ED667715F3622BE571405441B4
    echo "
--- START YOUR MESSAGE ---
Hello world,
This is a super secret message.
--- END YOUR MESSAGE ---
    " | gpg --encrypt --armor --recipient $RECIPIENT_FINGERPRINT
}

recieve-gpg-message(){
    __doc__='
    Decrypts a recieved message and prints cleartext to screen.
    '
    echo "
-----BEGIN PGP MESSAGE-----

hF4DFXuS5q76XyYSAQdAf4uiMVYQsRhBghcvgPanTbDE0lj3KwjZGEmSEeEv2yow
KuwdWdC+EGFAzw6aLn9SHSUHlNYwUw4mIqhyUTBpLFwJjuEc9Su/RprTY9FQGudC
0mgBit84kOmoDzP1uhsPXHe08pvFVBsREJ4+gVaVu13rgC16Ye/P1zsXSJ7lQHkt
GcRlVvtQGSkdzcHBBkXM/2uOFeKpV7qrI0TDVsisxb52p4M1kT7D1useG7JGtspX
Exsj6o2QYOkyvw==
=RQUc
-----END PGP MESSAGE-----
    " | gpg --decrypt
}
