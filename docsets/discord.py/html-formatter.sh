#!/bin/bash
files=$(fd --extension html)
for i in $files
do
	out=$(sed '/<div class="main-grid">/,/<main class="grid-item" role="main">/{//!d;};' $i)
	echo $out > $i
done


