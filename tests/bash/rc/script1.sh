if [ ! "$DID_SCRIPT1" = "" ]; then
   echo "already sourced"
   return
fi

echo "sourced script1"

DID_SCRIPT1=2
return
DID_SCRIPT1=3
