Terraform
=========

# Overview

Docset includes:

- [Terraform CLI and Language](https://www.terraform.io/docs)
- [All HashiCorp providers](https://registry.terraform.io/namespaces/hashicorp)

Maintained at [roberth-k/dash-docset-terraform](https://github.com/roberth-k/dash-docset-terraform).

The maintainer of the docset is not affiliated with HashiCorp.

# How to Build

The system must provide the following:

- bash
- git
- GNU Make
- Python 3.9

To build the docset, run:

```bash
git clone git@github.com:roberth-k/dash-docset-terraform.git
cd dash-docset-terraform
make docset
```

The docset will be available at `.build/latest/Terraform.docset` and the archive at `.build/latest/Terraform.tgz`.

# Previous Maintainers

- [bartoszj](https://github.com/bartoszj)
- [rolandjohann](https://github.com/rolandjohann)
- [f440](https://github.com/f440)
- [dazoakley](https://github.com/dazoakley)
