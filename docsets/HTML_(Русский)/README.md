# HTML (Russian) docset

Maintainer: [Omogobicoyu](https://github.com/Omogobicoyu).
Generation script and frozen example sources:
https://github.com/Omogobicoyu/html-forms-docset/tree/main/builder

To build from source, clone the generation repository first:

```sh
git clone https://github.com/Omogobicoyu/html-forms-docset.git
cd html-forms-docset
python -m pip install -r builder/requirements.txt
python builder/build.py --output dist
```

Copy `dist/HTML_RU.tgz` here as `HTML_(Русский).tgz`. The archive contains the
`HTML_(Русский).docset` bundle. The leading slash in `docset.json`'s version hides
the packaging date from the displayed version of HTML's living standard.

# Building HTML (Русский)

Maintainer: [Omogobicoyu](https://github.com/Omogobicoyu).

This is an unofficial Russian translation of the MDN HTML documentation snapshot
used by the original HTML revision 157 docset (mirrored 2026-10-16). It is not a
Mozilla or Kapeli release. The translation is mostly machine-generated with Argos
Translate en-ru 1.9; 233 introductory paragraphs came from mdn/translated-content.
Technical wording can be inaccurate. Original MDN code examples are preserved.

The `<form>` article links, through a collapsed practical-example section, to an
original educational PHP/MySQL portal. The example contains commented PHP/HTML/CSS,
a phone-number input mask, an offline phpMyAdmin GUI guide, and downloadable source.
The PHP/JS source is escaped text: it does not execute inside the docset. Running
the portal requires a separate local PHP/MySQL installation such as Open Server
Panel. The included SQL creates a fresh teaching schema; it contains no user data.

## Rebuild

Prerequisites: Python 3.12 or later and the packages listed in `requirements.txt`.
The script runs on Windows, macOS and Linux. PHP/MySQL and a translation model are
not required to package this frozen translation.

From the repository root:

```sh
python -m pip install -r builder/requirements.txt
python builder/build.py --output dist
```

The script downloads the previously published translated input from this immutable
URL, verifies SHA-256, and extracts it without following links or unsafe paths:

https://raw.githubusercontent.com/Omogobicoyu/html-forms-docset/2737dd5140181b94a91b0b0efeac4054fbcf7f70/HTML_RU.tgz

Expected SHA-256:

```text
f65e347d644670712522e8cc4d99f5b8ca519d40eb19167d8fe2eb2ccb6bf952
```

This is a rebuild from already translated HTML, not a new translation pass.
The frozen input contains the openly licensed `Documents` tree and our own index,
not Kapeli's restricted search metadata. The index is recreated from those recorded
entries, labels are normalized, paths and fragments are checked, and invalid
fragment targets fall back to their existing article. MDN's original code blocks
must remain unchanged. The stylesheet removes web navigation and sidebars for a
narrow offline documentation viewer without deleting article content.

Remote mdnplay frames are rebuilt locally from the compressed HTML/CSS/JS already
recorded in their original URLs. Optional online audio/video is retained as labelled
links, without automatic network loading. Missing optional webfonts fall back to
available local/system fonts. Additional MDN images are frozen under `offline-assets/`
with source URLs and SHA-256; the HTML `<pre>`/`<textarea>` examples are unchanged.

For a build without downloading the input again:

```sh
python builder/build.py --base-archive /path/to/HTML_RU-2026.11.17.2.tgz --output dist
```

Choose an output directory without an existing docset. Outputs:

- `dist/HTML_(Русский).docset/`: complete Dash/Zeal bundle.
- `dist/HTML_RU.tgz`: compressed installable bundle.
- `dist/HTML_RU-build-report.json`: counts, checks and SHA-256.
- `dist/SHA256SUMS`: archive checksum.

`site/` is the exact 2026-11-19 site snapshot, including centered authentication
forms, the phone mask and Russian code comments. `site-manifest.json` distinguishes
the current site files from the supplemental `database.sql`. The builder checks
every input hash and round-trips both HTML-escaped code and every ZIP entry.
To update this example deliberately, replace the relevant source files and update
the manifest; the builder must not silently package a different source snapshot.

## Licenses and sources

- MDN prose and this derivative translation: Mozilla Contributors, CC BY-SA 2.5 or
  a later version. Every translated article retains its source link and a notice
  that it was translated. See `LICENSES.txt` inside the bundle and
  https://developer.mozilla.org/en-US/docs/MDN/Writing_guidelines/Attrib_copyright_license.
- Russian introductory text: https://github.com/mdn/translated-content.
- MDN client resources: MPL-2.0, source https://github.com/mdn/fred. The full MPL text
  is retained inside the bundle. HTML5 logo: W3C, CC BY 3.0,
  https://www.w3.org/html/logo/.
- Original build scripts and teaching example: MIT, `LICENSE-MIT.txt`.
- Bootstrap 5.3.3: MIT, `BOOTSTRAP-LICENSE.txt`, source
  https://github.com/twbs/bootstrap/tree/v5.3.3.
- PT Sans: the included SIL Open Font License, `site/assets/fonts/OFL.txt`.
- Additional MDN content images retain the MDN content license. The shared
  `favicon72.png` is from https://github.com/mdn/shared-assets; see that repository's
  https://github.com/mdn/shared-assets/blob/main/LICENSE.md.

## Known limitations

- Most prose is machine-translated; reports of inaccurate terminology are welcome
  at https://github.com/Omogobicoyu/html-forms-docset/issues.
- This release is a frozen documentation snapshot, not a continuously synchronized
  copy of the live MDN site. External source/citation links and optional audio/video
  links require internet access. A few upstream error/link demonstrations deliberately
  request nonexistent image filenames; those failures are part of their examples.
- Native Dash import must still be tested on macOS; packaging on Windows cannot
  establish that result. Automated browser/offline checks are reported separately.
- A contribution is a request for maintainer review, not a guarantee of inclusion.
