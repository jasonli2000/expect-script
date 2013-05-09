#! /bin/sh
# find out the global path
globalDir=`dirname ${gtmgbldir}`
echo "global dir is $globalDir"
routineDir=`echo $gtmroutines | cut -d' ' -f1 | cut -d'(' -f2 | cut -d')' -f1 | cut -d',' -f1`
echo "routine dir is ${routineDir}"
curDT=`date +%m_%d_%YT%H_%M_%S`
backupFile=$HOME/backup/VistA-M.$curDT.tar.gz
backupLog=$HOME/backup/VistA-M.$curDT.log
echo "backup file is $backupFile"
echo "backup log is $backupLog"
# tar all the routines
# and all globals
tar czfv $backupFile $globalDir $routineDir 2>&1 > $backupLog
