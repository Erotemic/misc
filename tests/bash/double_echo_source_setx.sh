#!/usr/bin/env bash
__doc__="
Why do I get two plus characters ('+') when I source this bash script versus
running it with bash versus executing it line by line?
"

echo '
#!/usr/bin/env bash
# This is a bash file I will source

set -x
echo "hello world"
{ set +x; } 2>/dev/null

mkdir -p bookkeeping && touch foo
' > mwe_script.sh



source mwe_script.sh


bash mwe_script.sh
