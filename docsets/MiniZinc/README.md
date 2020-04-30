MiniZinc Docset
=======================

- __Docset Description:__
MiniZinc is a free and open-source constraint modeling language. You can use MiniZinc to model constraint satisfaction and optimization problems in a high-level, solver-independent way, taking advantage of a large library of pre-defined constraints.

- __Author:__ Matias Agelvis (https://github.com/Agelvie)

- Instructions to generate the docset:
    - Fetch the MiniZinc documentation from: [https://github.com/MiniZinc/minizinc-doc](https://github.com/MiniZinc/minizinc-doc)
    - Run `make html` to generate the whole html documentation.
    - Fetch Dashing [https://github.com/technosophos/dashing](https://github.com/technosophos/dashing) and follow the instructions to generate the docset file from the html documentation found at `minizinc-doc-develop/en/_build/html`