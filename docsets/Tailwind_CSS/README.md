# Tailwind CSS Docset

This docset contains the Tailwind CSS v4 documentation. It is generated from
the official documentation at [tailwindcss.com/docs][1] and includes the
versioned v3 and earlier archives listed in [`docset.json`][2] for users who
need the legacy documentation.

## Docset Maintainer

[Akinori Musha](https://github.com/knu)

## Generating the v4 docset

The v4 generator is maintained in
[`knu/docset-tailwindcss`][3]. Clone that repository and follow its
[`README.md`][4] to build the current docset.

The generator tracks the current Tailwind CSS v4 documentation and handles the
v4 site structure, including its generated assets and searchable sections.

Report generation issues to the [generator issue tracker][5]. Report Dash
packaging or metadata issues in this repository.

## Legacy versions

Older archives remain available under `versions/` and are intentionally kept
for projects that cannot yet move to Tailwind CSS v4. Tailwind CSS v4 targets
Safari 16.4+, Chrome 111+, and Firefox 128+; projects that require older
browsers should continue using the v3.4 archive.

[1]: https://tailwindcss.com/
[2]: ./docset.json
[3]: https://github.com/knu/docset-tailwindcss
[4]: https://github.com/knu/docset-tailwindcss/blob/main/README.md
[5]: https://github.com/knu/docset-tailwindcss/issues
