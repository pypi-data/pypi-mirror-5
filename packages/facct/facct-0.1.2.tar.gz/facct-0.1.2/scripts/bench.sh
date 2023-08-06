#!/bin/bash
script_root=$(dirname $(realpath $0))
app_root=$(dirname $script_root)
export PYTHONPATH=$PYTHONPATH:$app_root
bench_py="$(ls $app_root/*/bench.py)"
for cmd in 'python' 'python3'; do 
    echo "$cmd:"
    $cmd "$bench_py" -o corp_ref
    $cmd "$bench_py" -o figerson -b
    $cmd "$bench_py" -o toto
    $cmd "$bench_py" -o tutu
done
