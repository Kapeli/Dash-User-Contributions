# Effect Docset

[Effect](https://effect.website/) is a powerful TypeScript library for building production-ready applications with features like typed errors, dependency injection, concurrency, and more.

## Author

Community contribution (not affiliated with the Effect team).

## Generation Instructions

### Prerequisites

- [dashing](https://github.com/technosophos/dashing) - Install via `brew install dashing` or `go install github.com/technosophos/dashing@latest`
- `wget` for mirroring the documentation

### Steps

1. **Download the documentation:**

   ```bash
   wget --mirror --convert-links --adjust-extension --page-requisites \
        --no-parent https://effect-ts.github.io/effect/
   ```

2. **Copy `dashing.json`** from this directory to your working directory.

3. **Build the docset:**

   ```bash
   dashing build effect-ts.github.io/effect --source effect-ts.github.io/effect
   ```

4. **Archive for distribution:**

   ```bash
   tar --exclude='.DS_Store' -cvzf Effect.tgz Effect.docset
   ```

## Notes

- The Effect documentation is generated from TypeDoc and uses the "just-the-docs" Jekyll theme
- The docset includes all Effect ecosystem packages: `effect`, `@effect/platform`, `@effect/cli`, `@effect/cluster`, `@effect/sql`, and more
- Approximately 13,700+ entries are indexed including Functions, Interfaces, Types, Classes, Namespaces, and Sections

## Known Issues

None currently known. Please report docset generation issues at [Dash-User-Contributions](https://github.com/Kapeli/Dash-User-Contributions/issues).
