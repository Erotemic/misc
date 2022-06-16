"""

Downloads require manual interaction:

https://iuu.xview.us/download-links

https://xview3downloads.xview.us/labels/validation.csv
https://xview3downloads.xview.us/labels/train.csv
https://xview3downloads.xview.us/shoreline/train.tar.gz
https://xview3downloads.xview.us/shoreline/validation.tar.gz

mkdir -p $HOME/data/dvc-repos/xview3/images
cd $HOME/data/dvc-repos/xview3/images

mv $HOME/Downloads/tiny.txt  $HOME/data/dvc-repos/xview3/images
mv $HOME/Downloads/train.txt   $HOME/data/dvc-repos/xview3/images
mv $HOME/Downloads/validation.txt $HOME/data/dvc-repos/xview3/images

sudo apt install aria2
aria2c --input-file=tiny.txt --auto-file-renaming=false --continue=true --dir=./tiny --dry-run=false
aria2c --input-file=train.txt --auto-file-renaming=false --continue=true --dir=./train --dry-run=false
aria2c --input-file=validation.txt --auto-file-renaming=false --continue=true --dir=./validation --dry-run=false
"""
