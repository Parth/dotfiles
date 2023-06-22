#!/bin/bash
# test_commits.sh

while read -r rev; do
    # git checkout "$rev"
    echo $rev
   du -sh .
    # du -sh *
done < <(git rev-list 3d173732fcba5ebf6d2a3278f910b64be73e1943 681e62d2ac243da27924c5a610a2bc087f8f8a3c)
