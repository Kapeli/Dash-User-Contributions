# GitHub Actions docset

Build requirements:
* `ruby` to generate HTML
* `dashing` to build docset
* `docker` to create the archive

Build instructions:
```shell
git clone https://github.com/toy/github-actions-docset-builder.git
cd github-actions-docset-builder
bundle install
bundle exec rake
```

Scripts created by [Ivan Kuchin](https://github.com/toy)

Documentation is licensed under Creative Commons Attribution 4.0 (see [GitHub documentation LICENSE](GitHub%20documentation%20LICENSE.txt))
