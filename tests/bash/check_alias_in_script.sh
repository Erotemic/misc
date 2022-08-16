#!/bin/bash
__doc__="
This is a MWE illustrating an issue where using 'bash -c' to source a file that
sources another file does not seem to work how I would expect it. 

References:
    https://stackoverflow.com/questions/73378135/sourcing-bash-file-is-not-exporting-its-definitions-when-running-with-bash-c

Requires:
    sudo apt install cowsay
"
TEMP_DPATH=$(mktemp -d)


# Write a bash file containing some definitions
DEF_FPATH=$TEMP_DPATH/definitions.sh
echo '
#!/bin/bash
echo "[definitions] start"
alias mydef=cowsay
echo "[definitions] finish"
' > "$DEF_FPATH"


# Write a bash file containing some definitions
USAGE_FPATH=$TEMP_DPATH/usage.sh
echo '
#!/bin/bash
echo "[usage] about to source definitions"
source "'"$TEMP_DPATH"/definitions.sh'"
echo "[usage] about to use the definition"
mydef "hello world"
echo "[usage] finished"
' > "$USAGE_FPATH"


echo "Check DEF_FPATH looks ok"
echo "==============="
echo "DEF_FPATH = $DEF_FPATH"
echo "==============="
cat "$DEF_FPATH"
echo "==============="
echo ""
echo ""


echo "Check USAGE_FPATH looks ok"
echo "==============="
echo "USAGE_FPATH = $USAGE_FPATH"
echo "==============="
cat "$USAGE_FPATH"
echo "==============="
echo ""
echo ""



echo ""
echo ""
echo "Variant #1: Execute with source (this works)"
echo "-------------------"
source "$USAGE_FPATH"
echo "-------------------"


echo ""
echo ""
echo "Variant #2: Execute with bash -c (this fails)"
echo "--------------------"
bash -c "source '$USAGE_FPATH'"
echo "--------------------"
