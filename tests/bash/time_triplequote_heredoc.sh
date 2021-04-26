

echo "\nTIME TRIPLE QUOTES"
time for a in `seq 1000`; do ( source rc/triplequote_script.sh; ); done

echo "\nTIME STANDARD QUOTES"
time for a in `seq 1000`; do ( source rc/singlequote_script.sh; ); done


# Yeah, it does seem to make some small difference :(


time for a in `seq 100`; do ( source ~/local/init/freshstart_ubuntu.sh; ); done
#sed 's/"""/"/g' ~/local/init/freshstart_ubuntu.sh > /tmp/foo.sh
#time for a in `seq 100`; do ( source /tmp/foo.sh; ); done


#sed 's/"""/"/g' ~/local/init/freshstart_ubuntu.sh | sed "s/'''/'/g" > foo
#mv foo ~/local/init/freshstart_ubuntu.sh
#sed 's/"""/"/g' ~/local/init/utils.sh | sed "s/'''/'/g" > foo
#mv foo ~/local/init/utils.sh

time for a in `seq 100`; do ( source ~/local/init/utils.sh; ); done
#time for a in `seq 100`; do ( source $HOME/tmp/foo.sh; ); done
#cat  $HOME/tmp/foo.sh
#cat  ~/local/init/utils.sh
#cat  $HOME/tmp/foo.sh

