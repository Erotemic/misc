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

    # Edit this key to indicate that you trust it. You can skip this step but
    # if you skip it will ask you if you trust the key each time before you try
    # to encrypt a message for it.
    gpg --list-keys --fingerprint --with-colons "$RECIPIENT_FINGERPRINT" | \
        sed -E -n -e 's/^fpr:::::::::([0-9A-F]+):$/\1:6:/p' | \
        gpg --import-ownertrust
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





consise-version-with-filesystem(){
    __doc__="
    For copy / pasting in chats
    "
    # For more info
    # https://github.com/Erotemic/misc/blob/d0c679b0ead85136613f22339a8aff1f93573269/learn/send_me_a_gpg_message.sh
    RECIPIENT_FINGERPRINT=4AC8B478335ED6ED667715F3622BE571405441B4
    gpg --recv-keys --keyserver hkp://keyserver.ubuntu.com $RECIPIENT_FINGERPRINT
    gpg --list-keys --fingerprint --with-colons "$RECIPIENT_FINGERPRINT" | \
        sed -E -n -e 's/^fpr:::::::::([0-9A-F]+):$/\1:6:/p' | \
        gpg --import-ownertrust
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


consise-version-in-docker-raw(){
    __doc__="
    This variant of the command will run everything in docker
    "
    # For more info
    # https://github.com/Erotemic/misc/blob/0869242189a9b5415dc44c829b80e9f2ce96132a/learn/send_me_a_gpg_message.sh
    docker create --name tmp-gpg-container --rm -it ubuntu
    docker start tmp-gpg-container
    docker exec tmp-gpg-container bash -c "apt-get update && apt-get -y install gnupg2"
    docker exec tmp-gpg-container bash -c '
        RECIPIENT_FINGERPRINT=4AC8B478335ED6ED667715F3622BE571405441B4
        gpg --recv-keys --keyserver hkp://keyserver.ubuntu.com $RECIPIENT_FINGERPRINT
        gpg --list-keys --fingerprint --with-colons "$RECIPIENT_FINGERPRINT" | \
            sed -E -n -e '\''s/^fpr:::::::::([0-9A-F]+):$/\1:6:/p'\'' | \
            gpg --import-ownertrust
        echo "
        --- START YOUR MESSAGE ---
        Hello world,
        This is a super secret message.
        --- END YOUR MESSAGE ---
        " | gpg --encrypt --armor --recipient $RECIPIENT_FINGERPRINT
    '
    docker stop tmp-gpg-container
}


consise-version-in-docker-simple(){
    __doc__="
    This variant will use a preconfigured docker image on dockerhub to make the
    comand super concise at the expense of a small bit of obfuscation.

    SeeAlso:
        ~/misc/learn/send_me_a_gpg_message.dockerfile
    "
    # For more info
    # https://github.com/Erotemic/misc/blob/0869242189a9b5415dc44c829b80e9f2ce96132a/learn/send_me_a_gpg_message.sh
    echo "
    --- START YOUR MESSAGE ---
    Hello world,
    This is a super secret message.
    Paste whatever you want to say in here, and run the command to encrypt it.
    Then send Jon the output. Only he will be able to read it.
    --- END YOUR MESSAGE ---
    " | docker run -i erotemic/send-erotemic-a-gpg-message:latest
}


consise-version-with-stdout(){
    __doc__="
    For copy / pasting in chats
    "
    # The following snippet can be modified to send Jon an encrypted message
    # For more info about what this is doing see:
    # https://github.com/Erotemic/misc/blob/67573cf63cceaa37645c0df4d686c34a36a19c27/learn/send_me_a_gpg_message.sh
    RECIPIENT_FINGERPRINT=4AC8B478335ED6ED667715F3622BE571405441B4
    gpg --recv-keys --keyserver hkp://keyserver.ubuntu.com $RECIPIENT_FINGERPRINT
    gpg --list-keys --fingerprint --with-colons "$RECIPIENT_FINGERPRINT" | \
        sed -E -n -e 's/^fpr:::::::::([0-9A-F]+):$/\1:6:/p' | \
        gpg --import-ownertrust
    echo "
    --- START YOUR MESSAGE ---
    Hello world,
    This is a super secret message.
    --- END YOUR MESSAGE ---
    " | gpg --encrypt --armor --recipient $RECIPIENT_FINGERPRINT
    # Send me the output from the above command
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

hF4DFXuS5q76XyYSAQdAjDxim/vUtnN+R9XfnLwCBEmBQYhDQ1j2BvIYQOieF3sw
jVirBMYThjADN620l7wyZHCpb44L7wifPf+tOo86oTrCArz/VaKVj6l7oSfCX709
0okBEy/NeqBPdvORPpI1Cx07UZQYuBGK4sgEtTgrQ67jid+VS6HATnpGdd5iUz1f
xHMre2NrAWF5kupxu9nBrnjKtq2vUapX2lLiIkP0gb5mxs6tcMrZ2+/t6EyCZzE+
tJvjIla8gMDN0wods1aezO5Vwbb5aUqkW+9sNEjUqB/f73iYoo5HS91d6g==
=ydZh
-----END PGP MESSAGE-----
    " | gpg --decrypt
}
