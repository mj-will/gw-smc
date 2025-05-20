#!/usr/bin/env bash

result_file=$1
result_dir=$(dirname $result_file)
corner_file=${result_dir}/corner.png
injection_file=GW190425-like.json

echo "Plotting corner plot for ${result_file}"
echo "Output file: ${corner_file}"
python plot_single_result.py --result $result_file --filename ${corner_file} --injection ${injection_file}
