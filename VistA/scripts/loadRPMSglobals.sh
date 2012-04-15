#! /bin/sh
rm -f mump.load
for global in /opt/git/VistA-Variant/RPMS/Packages/*/Globals/*.zwr
do
    echo $global >> mump.load
    mupip load -format=zwr \"${global}\" >> mump.load 2>&1
done
