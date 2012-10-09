#! /bin/sh
sed 's#\[?1l>##g' < $1 | sed 's#\[C##g' | sed 's#\[[AC]##g' | sed 's#\[?1h=##g' #| sed 's##\r#g'
#sed 's#\[?1l>##g' < $1 | sed 's#\[C##g' | sed 's#\[[AC]##g' | sed 's#\[?1h=##g' | sed 's##\r#g'
