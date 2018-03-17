# Numba

* [Who am I?](https://github.com/singularitti)

* Docset description from [its official website](http://numba.pydata.org):

  > Numba gives you the power to speed up your applications with high performance functions written directly in Python. With a few annotations, array-oriented and math-heavy Python code can be just-in-time compiled to native machine instructions, similar in performance to C, C++ and Fortran, without having to switch languages or Python interpreters.
  >
  > Numba works by generating optimized machine code using the LLVM compiler infrastructure at import time, runtime, or statically (using the included pycc tool). Numba supports compilation of Python to run on either CPU or GPU hardware, and is designed to integrate with the Python scientific software stack.
  >
  > The Numba project is supported by Anaconda, Inc. (formerly known as Continuum Analytics) and [The Gordon and Betty Moore Foundation (Grant GBMF5423)](https://www.continuum.io/blog/developer-blog/gordon-and-betty-moore-foundation-grant-numba-and-dask).

* Complete instructions on how to generate the docset:
  * `doc2dash 2.2.0` [package](https://pypi.python.org/pypi/doc2dash) and `Sphinx 1.6.2` [package](http://www.sphinx-doc.org/en/master/)

  * You could download the initial HTML documentation for the docset from [here](https://github.com/numba/numba), just run

    ```shell
    git clone git@github.com:numba/numba.git
    ```

    to clone the repo to your local machine. Then run

    ```shell
    cd numba/docs
    make html
    doc2dash -n Numba -u http://numba.pydata.org -v -A -i numba_blue_icon_rgb.png .
    ```

    where `numba_blue_icon_rgb.png` can be found under `path/to/cloned/numba/repo/docs/_static`.
