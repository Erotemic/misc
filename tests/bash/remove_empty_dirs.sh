#!/usr/bin/env bash
__doc__='
References:
    https://www.cyberciti.biz/faq/howto-find-delete-empty-directories-files-in-unix-linux/
'

find . -empty -type d -delete
