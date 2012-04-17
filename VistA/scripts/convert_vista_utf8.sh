#! /bin/sh
gitrep=$1
for file in ${gitrep}/Packages/*/Routines/*.m
do
  echo "processing $file....."
  iconv -f latin1 -t utf-8 -o "$file.utf8" "$file"
  mv "$file.utf8" "$file"
done

for file in ${gitrep}/Packages/*/Globals/*.zwr
do
  echo "processing $file....."
  iconv -f latin1 -t utf-8 -o "$file.utf8" "$file"
  mv "$file.utf8" "$file"
done
