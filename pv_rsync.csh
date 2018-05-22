#!/bin/csh

set FROM=$1
set TO=$2

echo "Now syncing from $FROM to $TO ..."
echo "Press enter to continue:  "

set r = $<

if ( $r != "") then 
    echo "exit 1"
endif

if ( -e $FROM/index.sqlite.db ) then
    if ( -e $TO ) then
        echo rsync --size-only -arzvh $FROM $TO
        rsync --size-only -arzvh $FROM $TO
    endif
endif

