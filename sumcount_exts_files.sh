#!/usr/bin/env bash

declare -A ext_count

while IFS= read -r -d '' file; do
    name="${file##*/}"
    if [[ "$name" == *.* ]]; then
        ext="${name##*.}"
        ext="${ext,,}"      # lowercase
    else
        ext="[no_ext]"
    fi
    ((ext_count["$ext"]++))
done < <(find . -type f -print0)

for ext in "${!ext_count[@]}"; do
    printf "%6d %s\n" "${ext_count[$ext]}" "$ext"
done | sort -nr
