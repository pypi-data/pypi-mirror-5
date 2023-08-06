#!/bin/bash
bench_py="$(ls $(dirname $0)/../*/bench.py)"
for cmd in 'python' 'python3'; do 
    echo "$cmd:"
    $cmd "$bench_py" -o corp_ref
    $cmd "$bench_py" -o figerson -b
    $cmd "$bench_py" -o toto
    $cmd "$bench_py" -o tutu
done
