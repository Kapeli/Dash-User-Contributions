Terraform Docset
=======================

https://terraform.io/docs/

Contriubuted by [rolandjohann](https://github.com/rolandjohann/terraform-dash-doc-generator.git)

## Building the docsets

```sh
git clone https://github.com/rolandjohann/terraform-dash-doc-generator.git
cd terraform-dash-doc-generator
./build_until_0.9.sh # to build all docsets until v0.9.11
./build_current_from_0.10.sh <version> # to build current state of https://github.com/hashicorp/terraform-website.git and move to build/<version>
```

## Old version (< 0.10.0)

ref. [README.deprecated.md](README.deprecated.md)

## Old version (< 0.6.0)

ref. [README.old.md](README.old.md)
