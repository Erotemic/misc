#!/usr/bin/env bash
__doc__="
bash ~/misc/tests/bash/bash_filename.sh
"
source ~/local/init/utils.sh

echo "BASH_SOURCE = "
bash_array_repr "${BASH_SOURCE[@]}"

# Use bash magic to get the path to this file if running as a script
THIS_DPATH=$(python3 -c "import pathlib; print(pathlib.Path('${BASH_SOURCE[0]}'))")
echo "THIS_DPATH = $THIS_DPATH"
