MiniZinc Docset
=======================

- __Docset Description:__
MiniZinc is a free and open-source constraint modeling language. You can use MiniZinc to model constraint satisfaction and optimization problems in a high-level, solver-independent way, taking advantage of a large library of pre-defined constraints.

- __Author:__ *Originally* Matias Agelvis (https://github.com/Agelvie), *Improved by* Alexander Ronald Altman (https://github.com/pthariensflame)

- Instructions to generate the docset:
    - Fetch the MiniZinc documentation from: [https://github.com/MiniZinc/minizinc-doc](https://github.com/MiniZinc/minizinc-doc)
    - Follow `README.md` from there to generate the complete documentation in `en` including the standard library.
	- Copy `icon@2x.png` from here into `en/_build` and rename the copy `icon32x32.png`.
    - Fetch Dashing [https://github.com/technosophos/dashing](https://github.com/technosophos/dashing) and follow the instructions to generate the docset file from the html documentation found at `en/_build/html`, using the following `dashing.json`:

```json
{"name":"MiniZinc","package":"MiniZinc","index":"index.html","selectors":{"title":{"type":"Guide","regexp":"\\s*— The MiniZinc Handbook 2.4.3","replacement":""},"h1":{"type":"Section","regexp":"\\s*¶","replacement":""},"h2":{"type":"Section","regexp":"\\s*¶","replacement":""},"h3":{"type":"Section","regexp":"\\s*¶","replacement":""},"h4":{"type":"Section","regexp":"\\s*¶","replacement":""},"h5":{"type":"Section","regexp":"\\s*¶","replacement":""},"h6":{"type":"Section","regexp":"\\s*¶","replacement":""},"dt code.descname":"Option","div.highlight pre":[{"requiretext":"^annotation","type":"Annotation","regexp":"^annotation'?([^()':\\s]+)'?(\\((?:.|\\n|\\r)+)?","replacement":"$1","matchpath":"lib.*\\.html"},{"requiretext":"^(?:predicate|test)","type":"Procedure","regexp":"^(?:predicate|test)'?([^()':\\s]+)'?\\((?:.|\\n|\\r)+","replacement":"$1","matchpath":"lib.*\\.html"},{"requiretext":"^function","type":"Function","regexp":"^function[^()':]*:'?([^()':\\s]+)'?\\((?:.|\\n|\\r)+","replacement":"$1","matchpath":"lib.*\\.html"},{"requiretext":"^opt","type":"Global","regexp":"^opt[^()':]*:'?([^()':\\s]+)'?","replacement":"$1","matchpath":"lib.*\\.html"}]},"ignore":["Index — The MiniZinc Handbook 2.4.3","Index","Symbols","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","Parameters","Functions and Predicates"],"icon32x32":"../icon32x32.png","allowJS":true,"ExternalURL":"https://www.minizinc.org/doc-2.4.3/en"}
```

(replacing all occurances of `2.4.3` with the version you're building for).
