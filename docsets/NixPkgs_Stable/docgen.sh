#!/bin/bash

wget -p https://nixos.org/manual/nixpkgs/stable/index.html

sed -Ei '' \
  -e '/<header>/,/<\/header>/d' \
  -e '/<footer>/,/<\/footer>/d' \
  -e 's/<section class="generic-layout docbook-page">(.*<section class="chapter">)/\1/' \
  nixos.org/manual/nixpkgs/stable/index.html

dashing build --source=nixos.org

tar -czvf NixPkgs_Stable.tgz nixpkgs_stable.docset
