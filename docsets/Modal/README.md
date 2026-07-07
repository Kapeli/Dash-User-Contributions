Modal Dash Docset
=================

- __Docset Description__:
  - Offline Dash docset for the Modal platform docs, including the main docs site, API reference, examples, and GPU glossary.

- __Author__:
  - [sheikheddy](https://github.com/sheikheddy)

- __Upstream docs__:
  - [https://modal.com/docs](https://modal.com/docs)
  - [https://modal.com/gpu-glossary/readme](https://modal.com/gpu-glossary/readme)

- __Prerequisites__:
  - Python 3
  - `wget`
  - `sips` on macOS for generating the docset icons

- __How the docset was generated__:
  - Mirror the Modal docs and GPU glossary HTML.
  - Strip JavaScript and Typekit references so the mirrored docs are usable offline.
  - Rewrite absolute Modal links to local relative paths where mirrored files exist.
  - Build a Dash search index from page titles, H1s, and H2/H3 section anchors.
  - Package the result as `Modal.docset` and archive it into `Modal.tgz`.

Example command:

```bash
python3 build_modal_docset.py --keep-build
```

Generated artifacts:

```text
Modal.docset
Modal.tgz
Modal.tgz.sha256
Modal.xml
```

- __Known limitations__:
  - Some links that intentionally leave the documentation site, such as login or pricing links, remain online-only.
  - A few malformed upstream asset URLs currently return 404 during mirroring; the build tolerates those because the mirrored docs remain navigable offline.
