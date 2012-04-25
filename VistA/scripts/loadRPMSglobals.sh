#! /bin/sh
gitrep=$1
rm -f mump.load
for global in ${gitrep}/Packages/*/Globals/*.zwr
do
    echo $global >> mump.load
    mupip load -format=zwr \"${global}\" >> mump.load 2>&1
done
