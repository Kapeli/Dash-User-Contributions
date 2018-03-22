VERSION = 3.1

for i in classes/$VERSION/*.html; do
    sed -r -i 's/.+<div class="classContent">/<link rel="stylesheet" href="main.css"><div class="classContent" style="margin: 0; padding: 0; width: auto;">/' $i
    echo $i
done

cp main.css classes/$VERSION/

~/go/bin/dashing build