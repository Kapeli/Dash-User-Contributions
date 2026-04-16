Einops Dash Docset
==================

- __Docset Description__:
  - Offline Dash docset for the full [einops.rocks](https://einops.rocks/) documentation site, including tutorials, API reference, and the `einops.einsum` page.

- __Author__:
  - [sheikheddy](https://github.com/sheikheddy)

- __Upstream docs__:
  - [https://einops.rocks/](https://einops.rocks/)
  - [https://einops.rocks/api/einsum/](https://einops.rocks/api/einsum/)

- __Prerequisites__:
  - Python 3
  - `wget`
  - `sips` on macOS for generating docset icons

- __How the docset was generated__:
  - Mirror the full `einops.rocks` docs site.
  - Download the upstream Einops logo separately because the site favicon currently returns `404`.
  - Rewrite absolute `einops.rocks` links to local relative paths where mirrored files exist.
  - Build a Dash search index from page titles, H1 headings, and API/function section anchors.
  - Package the result as `Einops.docset` and archive it into `Einops.tgz`.

Example command:

```bash
python3 build_einops_docset.py --keep-build
```

Generated artifacts:

```text
Einops.docset
Einops.tgz
Einops.tgz.sha256
Einops.xml
```

- __Known limitations__:
  - Some decorative badges and external media embedded by the upstream site remain online-only.
  - The upstream `https://einops.rocks/images/favicon.png` reference currently returns `404`, so icon generation uses the published Einops logo instead.
