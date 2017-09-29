#!/bin/sh

# This script converts olf profile format (v0.46 and earlier) to the new format
# introduced in 0.47

PWD=$(pwd)
src="$1"

if test -z "$src"
then
    echo "usage: $0 <srcdir>"
    exit
fi

base=$(basename $src)
tgt="$PWD/$base"

if test -e "$tgt"
then
    echo "target exists ($tgt)"
    exit
fi

# ------------------------------------------------------------------------------
#
handle_dir(){

    local src="$1"
    local tgt="$2"

    local oldpwd=$(pwd)
    local d
    local f
    cd $src

    for d in */
    do
        if ! test -d "$d"
        then 
            continue
        fi
        echo "-> $tgt/$d"
        mkdir -p "$tgt/$d"
        handle_dir "$src/$d" "$tgt/$d"
        echo "<- $tgt/$d ($src)"
    done

    for f in $src/*.prof
    do
        echo "   $f"
        if ! test -e "$f"
        then
            continue
        fi
        handle_file "$src" "$tgt" "$(basename $f)"
    done

    for j in $src/*.json
    do
        if ! test -e "$j"
        then
            continue
        fi
        cp $j $tgt
    done
}


# ------------------------------------------------------------------------------
#
handle_file(){

    local src="$1"
    local tgt="$2"
    local fin="$3"

    local fout="$tgt/$fin"

    local OLD_IFS="$IFS"
    local IFS=","

    while read time name uid state event msg
    do
        if test "$event" = 'sync rel'
        then
            event='sync_rel'
        fi
        if test "$event" = 'sync abs'
        then
            event='sync_abs'
        fi
        echo "$time,$event,$name,,$uid,$state,$msg" >> "$fout"
    done < "$src/$fin"

    local IFS="$OLD_IFS"
    
}

# ------------------------------------------------------------------------------
#
mkdir -p "$tgt"
handle_dir "$src" "$tgt"

# ------------------------------------------------------------------------------

