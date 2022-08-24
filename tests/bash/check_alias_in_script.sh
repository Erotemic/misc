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
export MYDEF=cowsay
# DONT USE ALIASES THEY DO NOT EXPAND UNLESS expand_aliases in shopt is set!
# https://www.gnu.org/software/bash/manual/html_node/Aliases.html
alias mydef=cowsay
echo "[definitions] finish"
' > "$DEF_FPATH"


# Write a bash file containing some definitions
USAGE_FPATH=$TEMP_DPATH/usage.sh
echo '
#!/bin/bash
echo "[usage] about to source definitions"
#shopt -s expand_aliases
source "'"$TEMP_DPATH"/definitions.sh'"
echo "[usage] about to use the definition"
#shopt
#shopt
mydef "hello world"
#$MYDEF "hello world"
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
set +x
source "$USAGE_FPATH"
set +x
echo "-------------------"


echo ""
echo ""
echo "Variant #2: Execute with bash -c (this fails)"
echo "--------------------"
set +x
/bin/bash -c "source '$USAGE_FPATH'"
set +x
echo "--------------------"


echo ""
echo ""
echo "Variant #3: Execute with bash -ci (this works)"
echo "--------------------"
set +x
/bin/bash -ci "source '$USAGE_FPATH'"
set +x
echo "--------------------"


echo ""
echo ""
echo "Variant #4: Execute with bash -c with shopt -s expand_aliases (this works)"
echo "--------------------"
set +x
/bin/bash -ci "shopt -s expand_aliases && source '$USAGE_FPATH'"
set +x
echo "--------------------"
