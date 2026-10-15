EyalSec Docset
=======================

The user guide for [EyalSec](https://eyalsec.com): signing in, adding machines,
choosing what to watch, reading and filtering events, rules and templates,
running es-python, and the REST API. It is an offline copy of
https://eyalsec.com/docs.

#### Maintainer

Eyal Gabay, [@eyal-gabay](https://github.com/eyal-gabay) (I work on EyalSec).
Questions or a broken page: open an issue here and mention @eyal-gabay, or write
to support@eyalsec.com.

#### Generating the docset

The guide is written in Markdown, and the generator renders it with the same
Markdown settings the site uses, so each page matches its online version.

Prerequisites: Go 1.25 or newer and the `sqlite3` command-line tool.

The guide's Markdown source and the generator (`tools/docset`) live in
EyalSec's own repository, which is private, so the maintainer regenerates the
docset whenever the guide on the site changes. From the repository root:

```bash
go run ./tools/docset -contrib -ref <commit the site runs> -live https://eyalsec.com -out /tmp/eyalsec-docset
```

`/tmp/eyalsec-docset/EyalSec/` then holds this folder, the archive included.

The generator checks its work before writing anything:

- With `-live`, every page must match the guide served at
  https://eyalsec.com/docs (title, summary and text), so the docset is
  exactly what the site shows.
- No index entry may be empty or span lines, and every entry must point at a
  file and an anchor that exist.

#### What is indexed

| Type | Entries |
|------|---------|
| Guide | every page of the guide |
| Section | every heading on a page, also shown in the table of contents |
| Word | the terms in the glossary |
| Method | the REST API endpoints, for example `GET /api/get_all_machines/` |
| Option | es-python command-line flags |
| Environment | the environment variables that set the same options |

Links to pages outside the guide (pricing, contact) open the live site.

#### Known issues

None yet.
