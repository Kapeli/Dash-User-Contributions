Terraform Docset
=======================

https://terraform.io/docs/

Contributed by [rolandjohann](https://github.com/rolandjohann/terraform-dash-doc-generator.git)

## Building the docsets

### System Package Requirements

The following packages need to be available on the system for building the docset:

- ruby-dev
- libsqlite3-dev
- nodejs

On Ubuntu:
```text
sudo apt-get install ruby-dev build-essential patch ruby-dev zlib1g-dev liblzma-dev libsqlite3-dev rake libv8-dev nodejs
```

### Build Process

```sh
git clone https://github.com/rolandjohann/terraform-dash-doc-generator.git
cd terraform-dash-doc-generator
./build_until_0.9.sh # to build all docsets until v0.9.11
./build_current_from_0.10.sh <version> # to build current state of https://github.com/hashicorp/terraform-website.git and move to build/<version>
```

### Build Troubleshooting

In case the build process fails at the json package requiring bundler version 1.16.1 then locate the build directory
`/terraform-dash-doc-generator/terraform-website/content` and update the `bundler`:

```text
sudo gem install bundler -v 1.16.1
sudo bundle update
# Packages that could cause problems in the build process
sudo gem install json -v '1.8.6'
sudo gem install nokogiri -v '1.10.9'
sudo gem install sqlite3
```

## Old version (< 0.10.0)

ref. [README.deprecated.md](README.deprecated.md)

## Old version (< 0.6.0)

ref. [README.old.md](README.old.md)
