Pygments
=======================

* [Who am I?](https://github.com/singularitti)

* Docset description from [its official website](http://pygments.org):

  > Pygments is a generic syntax highlighter suitable for use in code hosting, forums, wikis or other applications that need to prettify source code. Highlights are:
  >
  > - a wide range of over 300 languages and other text formats is supported
  > - special attention is paid to details that increase highlighting quality
  > - support for new languages and formats are added easily; most languages use a simple regex-based lexing mechanism
  > - a number of output formats is available, among them HTML, RTF, LaTeX and ANSI sequences
  > - it is usable as a command-line tool and as a library
  > - ... and it highlights even Perl 6!

* Complete instructions on how to generate the docset:
  * `doc2dash 2.2.0` [package](https://pypi.python.org/pypi/doc2dash) and `Sphinx 1.6.2` [package](http://www.sphinx-doc.org/en/master/)

  * You could download the initial HTML documentation for the docset from [here](https://bitbucket.org/birkenfeld/pygments-main), just run

    ```shell
    hg clone ssh://hg@bitbucket.org/birkenfeld/pygments-main
    ```

    to clone the repo to your local machine. Then run

    ```shell
    cd pygments-main/doc/
    make html
    doc2dash -n Pygments -u http://pygments.org -v -A -i logo_only.png .
    ```

    where `logo_only.png` can be found under `path/to/cloned/repo/pygments-main/doc/_static`.

  ​
