# How To Send Jon a GPG Message

A [GPG](https://en.wikipedia.org/wiki/GNU_Privacy_Guard) message is a way to
send a message to someone, such that only they can read it. The catch is that
you need to be sure the public key you are using actually belongs to the person
you want to send the message to. My public key is
`4AC8B478335ED6ED667715F3622BE571405441B4`.

This can be corroborated by other posts I've made:

* https://keyserver.ubuntu.com/pks/lookup?search=4AC8B478335ED6ED667715F3622BE571405441B4&fingerprint=on&op=index
* https://bsky.app/profile/erotemic.bsky.social/post/3lgdmzp3p2k2m
* https://sigmoid.social/@erotemic/109540671404639989
* https://github.com/Erotemic

### Option 1: Using Docker 

To make the process as easy as possible, I've created a docker image 
[erotemic/send-erotemic-a-gpg-message](https://hub.docker.com/r/erotemic/send-erotemic-a-gpg-message) 
that has my public key registered and a simple entrypoint that encrypts a
message for me.

If you have docker on your system you can run the following command: 

```bash
echo "
--- START YOUR MESSAGE ---
Hello world,
This is a super secret message.
Paste whatever you want to say in here, and run the command to encrypt it.
Then send Jon the output. Only he will be able to read it.
For more info, see:
https://github.com/Erotemic/misc/blob/303d63cb09/learn/send_me_a_gpg_message.sh
--- END YOUR MESSAGE ---
" | docker run -i erotemic/send-erotemic-a-gpg-message:latest
``` 

This will write out a message that looks like this:

```
-----BEGIN PGP MESSAGE-----

hF4DFXuS5q76XyYSAQdAucAvJHGTsx+4xQCy5lS6MeXJB2Iwa8JcYQa3wjwJyVEw
Vs+ByI+ohOicx69H3To/SWoPjAbBg/3uJATo9YPMtHhNh4RbFQTmeL/WPzukT5DT
0sByAXAD0cA2hW/y5sce+PoYvf29VTEhr0w4qPuVXgH6YP8KpTEIEyD33+AJ81L4
r2GnBQACKi7VM064CcKnkKnKegXRr2mmz/xIAMtNSyceA4VFr1q8NtHxjWxgb1ud
pN+RNeyJAAzwg7q8pXdH9YsHnDOzEduLuBezOGCuCAo96GhgKZ/kW6nzT5hXfD3H
SBoSogdzamGmwQGOzGRj+6xZZjvNm1KaPjl1MJQ0fxqNz4MZU8vSuLQSnRnSxCIS
ixgcDd1qP8xK+PEOlRQhLLO3lYl0Yf4QLElAPRoSPfUdRzqWImWavcGrNacmrtRF
DAXIZj+0UGZvSoL/TssAPNMkWDCYY9dYN8/a1qOat3oAYf+KHSTrQovfNdH7JhGF
Brq4sY1PbMe4hCtKWJ0bCzLnl1Al
=Ymmx
-----END PGP MESSAGE-----
```

Then you can send that message to me over any communication channel. 
The only way to decrypt it is to have my secret key.


### Option 2: Using the GPG CLI in Debian / Ubuntu

If you want to use GPG explicitly you can take the following steps:

```bash

# Install GPG
sudo apt-get update 
sudo apt-get -y install gnupg2

# The key of the person you want to send a message to
RECIPIENT_FINGERPRINT=4AC8B478335ED6ED667715F3622BE571405441B4

# Get full public key information from a key server
gpg --recv-keys --keyserver hkp://keyserver.ubuntu.com $RECIPIENT_FINGERPRINT

# (optional) Mark that you trust the public key
gpg --list-keys --fingerprint --with-colons "$RECIPIENT_FINGERPRINT" | \
    sed -E -n -e 's/^fpr:::::::::([0-9A-F]+):$/\1:6:/p' | \
    gpg --import-ownertrust

# Encrypt the message
echo "
--- START YOUR MESSAGE ---
Hello world,
This is a super secret message.
--- END YOUR MESSAGE ---
" | gpg --encrypt --armor --recipient $RECIPIENT_FINGERPRINT

```
