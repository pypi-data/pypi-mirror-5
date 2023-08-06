#!/bin/bash
script_root=$(dirname $(realpath $0))
app_root=$(dirname $script_root)
export PYTHONPATH=$PYTHONPATH:$app_root
py_root=$(dirname $(ls $app_root/*/config.py))
domain=$(basename $py_root)
lang=fr
country=FR
LC=${lang}_${country}
po_dir=$app_root/po
mo_dir=$py_root/locale/$LC/LC_MESSAGES

if [ "$1" = "sav" ]; then
    rm -f $po_dir/$lang.po.bkup
    exit 0
fi
if [ ! "$1" = "mo" ]; then
    env PWD=$py_root xgettext --language=Python --keyword=_ --output=- \
            `find . -name "*.py"`| grep -v '^#'| \
            sed "s+\(charset\)=CHARSET+\1=UTF-8+;s+\(Language:\) +\1 $lang+" \
            > $app_root/po/$domain.pot

    if [ -f $po_dir/$lang.po ] && [ ! -f $po_dir/$lang.po.bkup ] ; then
        cp $po_dir/$lang.po $po_dir/$lang.po.bkup
    fi
    msginit -i $po_dir/$domain.pot --locale=$LC -o $po_dir/$lang.po --no-translator
fi

mkdir -p $mo_dir
iconv $po_dir/$lang.po -t=UTF-8 -f=ISO-8859-1 > $po_dir/$lang-utf8.po
msgfmt $po_dir/$lang-utf8.po -D $po_dir -o $mo_dir/$domain.mo --check-domain

# runtime test:
account_dir=$py_root/bench_infra/corp_ref/accounts/2013
env LANG=$LC python $py_root/generate_all.py -o corp_ref -d $account_dir
env LANG=$LC python3 $py_root/generate_all.py -o corp_ref -d $account_dir
env LANG=$LC python3 $py_root/bill/gen_tex.py -o corp_ref 022013.csv
