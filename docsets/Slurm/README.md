Slurm Docset
============

Author: [sheikheddy](https://github.com/sheikheddy)

This docset is generated from the public SchedMD Slurm documentation at <https://slurm.schedmd.com/>. The upstream documentation page identifies the current documentation as Slurm version 26.05.

Generation
----------

Prerequisites:

* `wget`
* Python 3
* ImageMagick `magick` or `convert` (for `icon.png` and `icon@2x.png`)

Download a local copy of the HTML documentation:

```bash
tmpdir=$(mktemp -d /tmp/slurm-docs-web.XXXXXX)
wget --mirror --page-requisites --adjust-extension --convert-links --no-parent \
  --domains=slurm.schedmd.com --execute robots=off \
  --reject-regex '(/archive/|/MISC[0-9]*/|/SC[0-9]*/|/SLUG[0-9]*/|\.pdf($|[?#]))' \
  --directory-prefix="$tmpdir" \
  https://slurm.schedmd.com/
```

Generate and archive the docset:

```bash
builddir=$(mktemp -d /tmp/slurm-docset-build.XXXXXX)
python3 scripts/generate-docset.py \
  --source-dir "$tmpdir/slurm.schedmd.com" \
  --build-dir "$builddir" \
  --archive Slurm.tgz \
  --icon-dir .
mkdir -p versions/26.05
cp Slurm.tgz versions/26.05/Slurm.tgz
```

Notes
-----

The generation script removes the hosted Google Custom Search widget and other active external resource tags so the documentation works offline in Dash, while leaving normal outbound documentation links intact.

Known bugs: none.
