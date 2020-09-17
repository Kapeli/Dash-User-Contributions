ggplot2
=======================

#### About

I'm Michael Peteuil, the original author of this docset. You can find me online
at https://github.com/mpeteuil or https://twitter.com/mpeteuil

## Generating the docset

#### Pre-requisites

In order to generate the docset you will need the R programming language and
the following R libraries installed: `ggplot2`, `hexbin`, `Hmisc`, `quantreg`,
`multcomp`, `mapdata`, `mapproj`, `maps`,
[devtools](https://github.com/hadley/devtools) and
[staticdocs](https://github.com/hadley/staticdocs). In addition, this
particular docset was generated with the useful
[dashing](https://github.com/technosophos/dashing) Dash documentation
generator tool. 

#### Online and offline ggplot2 documentation

ggplot2 documentation exists online at http://docs.ggplot2.org/, however it
can also be generated locally using
[devtools](https://github.com/hadley/devtools) and
[staticdocs](https://github.com/hadley/staticdocs). In order to do so you will
need to have `ggplot2` installed. Once you have all of the pre-requisites, you
can open up R and run `staticdocs::build_site(ggplot2)` where `ggplot2` is the
ggplot2 package's source. One variation might be
`staticdocs::build_site(devtools::as.package("/path/to/ggplot2"))`.

###### ggplot2 doc generation issues

While `staticdocs` is generating the `ggplot2` html documentation it may fail
with a message like _there is no package called ‘SOME_PACKAGE’_. If this
happens just run `install.packages("SOME_PACKAGE")` and try again.

#### Generating ggplot2 documentation with dashing

To use [dashing](https://github.com/technosophos/dashing) to generate the
ggplot2 docset, you must follow the [install directions for
dashing](https://github.com/technosophos/dashing#install). Once installed, all
you have to do is go to the directory that `staticdocs` compiled the ggplot2
documentation into and run `dashing build ggplot2` which will construct create
`ggplot2.docset`. You can then run the command `tar --exclude='.DS_Store' -cvzf
ggplot2.tgz ggplot2.docset` and you will have an updated ggplot2.tgz file.
