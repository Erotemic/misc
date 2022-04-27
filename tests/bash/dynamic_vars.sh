#!/bin/bash
# https://stackoverflow.com/questions/16553089/dynamic-variable-names-in-bash

key="custom_key"
val="custom_val"

# Set the variable pointed to by "key"
declare $key=$val

# Read the value of the varabile pointed to by key
loaded="${!key}"

echo "loaded = $loaded"
