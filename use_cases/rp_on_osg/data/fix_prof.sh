#!/bin/sh

base=`pwd`
tmpfile="/tmp/awk_tmp_$(id -u)"

awk_cmd='
BEGIN {
    FS=",";
    OFS=",";
}
{
    if ($1 == 1.0) {
        fix = substr($0, index($0, $2));
    }
    else {
        if (fix) {
            print $1,fix;
            fix="";
        }
        print;
    }
}
'

for sid in rp.session.*
do
    echo "$sid"
    cd "$base/$sid"

    for pid in pilot.*/
    do
        echo "    $pid"
        cd "$base/$sid/$pid"

        for prof in *.prof
        do
            if grep -qe '^1\.000' $prof
            then
                echo "        $prof"
                awk "$awk_cmd" $prof > $tmpfile
                mv $tmpfile $prof
            fi
        done
    done
done

cd $base

