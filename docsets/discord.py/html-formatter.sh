#!/bin/bash
#cd ~/.local/share/Zeal/Zeal/docsets/discord.py.docset
files=$(fd --extension html)
for i in $files
do
	out=$(sed '/<div class="main-grid">/,/<main class="grid-item" role="main">/{//!d;};' $i)
	echo $out > $i
done


