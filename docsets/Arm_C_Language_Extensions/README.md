# Arm C Language Extensions

This contribution generates an offline Dash docset for the
[Arm C Language Extensions (ACLE)](https://github.com/ARM-software/acle).
It is an unofficial adaptation maintained by
[Joey Teng](https://github.com/JoeyTeng); it is not produced, sponsored, or
endorsed by Arm.

The converter merges version-pinned public sources into one consistent API
reference layout. Each concrete callable page can include its signature,
maturity, architecture and compiler requirements, parameters, semantics,
instruction relationships, constraints, aliases, performance evidence, and
exact provenance. Missing source-backed facts remain visibly unresolved rather
than being presented as zero or empty values.

Public ACLE C/C++ data types are also rendered as searchable Dash `Type`
entries. Each type page preserves the exact typedef declaration and source
location from the pinned Clang resource headers. When the same spelling has
different declarations for distinct ISA families or preprocessor conditions,
the catalog retains those declarations separately rather than selecting one by
name alone. Type pages show header and availability facts, but deliberately do
not show instruction latency or throughput: those are properties of instruction
forms, not of a data type. Where a width is encoded by the public ACLE type
spelling, the page shows its fixed vector width and lane shape, or explicitly
labels SVE/SME types as scalable in terms of VL rather than inventing a fixed
width. Type pages also group source-backed function signatures for direct
cross-type conversions, scalar construction/insertion, and scalar extraction.
Every documented ACLE type token in a function signature, parameter row, or
result type links to its local Dash Type page. These groups are generated from
the pinned signatures as navigation aids; they do not claim identical value
semantics for every listed intrinsic.

The docset also generates clickable Dash `Guide` pages for every level of the
source taxonomy. A guide lists its child categories and the callables directly
assigned to it, allowing navigation such as MVE → Vector arithmetic → Add →
Addition. Data-width guides collect documented types with the same derived
fixed or scalable width group. To keep Dash's sidebar unambiguous, aliases are
shown on their canonical callable page but are not duplicated as sidebar search
index entries.

## Coverage

The generated catalog covers:

- Advanced SIMD (Neon);
- M-Profile Vector Extension (MVE, also known as Helium);
- Scalable Vector Extension (SVE and SVE2);
- Scalable Matrix Extension (SME and SME2); and
- general ACLE declarations such as barriers, system-register access, CRC,
  DSP, and CDE intrinsics.

Release, Beta, Alpha, and Unspecified entries are all retained and labeled.
Overloaded spellings remain searchable while each concrete signature gets a
stable page. Compiler requirements include source-backed feature macros and
version-scoped `-march` or `-mcpu` examples where available. For example, CRC
entries identify the `+crc` architecture feature instead of treating it as a
baseline AArch64 facility.

## Pinned sources

| Source | Revision | Purpose |
| --- | --- | --- |
| [Arm ACLE](https://github.com/ARM-software/acle/tree/62d9cbd68abb6d18dd8f06980da7758d9dbe0560) | `62d9cbd68abb6d18dd8f06980da7758d9dbe0560` (2026-08-25) | Primary semantics, availability, maturity, general ACLE declarations, and the Neon/MVE intrinsic databases |
| [Arm A-profile feature registry](https://documentation-service.arm.com/static/69402e206efc1635355c3bb2?token=) | `109697_2025_12_en`, version 1.0 (2025-12-12) | Factual minimum-architecture and ISA-dependency relationships only; no document prose, tables, images, or PDF are redistributed |
| [LLVM](https://github.com/llvm/llvm-project/tree/fef02d48c08db859ef83f84232ed78bd9d1c323a) | `llvmorg-22.1.1` at `fef02d48c08db859ef83f84232ed78bd9d1c323a` | Generated public declaration data, compiler-feature mappings, and LLVM scheduling-model estimates |
| [GCC manuals](https://gcc.gnu.org/onlinedocs/gcc-16.2.0/gcc/) | `16.2.0` | Version-scoped Arm and AArch64 compiler-option examples |
| [GCC validation source](https://github.com/gcc-mirror/gcc/tree/fcfb06e236d4d1689a6caf8e5409b078262af481) | `fcfb06e236d4d1689a6caf8e5409b078262af481` | Transient static sampled cross-check only; no GCC content is copied into the docset or archive |

ACLE uses continuous publication after its 2026Q1 release. The Dash feed
version is therefore `/62d9cbd68abb`: the immutable ACLE commit is the update
token, while Dash's leading-slash convention hides it as an internal snapshot
identifier instead of presenting it as an upstream release number.

### Performance evidence

Latency, reciprocal throughput, micro-op count, and execution-resource values
are included only when the converter can join an instruction form to an
applicable pinned LLVM 22.1.1 scheduling model. These values are compiler model
estimates produced by LLVM tooling, not measurements from physical hardware.
They are labeled per microarchitecture and never generalized across CPUs.

The model profiles cover Cortex-A55, Neoverse N1, Neoverse V1, Neoverse N2,
Cortex-M55, and Cortex-M85. A profile that LLVM marks incomplete is labeled as
partial. If LLVM 22.1.1 has no applicable model, including SME and SME2, the
page states that reason and publishes no invented value.

## Reproduce the docset

Requirements:

- CPython 3.14.2 exactly, as selected by `.python-version`;
- [uv](https://docs.astral.sh/uv/) with the committed `generator/uv.lock`;
- `clang-tblgen`, `llvm-mca`, and `llvm-mc` 22.1.1 from the pinned LLVM
  release; and
- network access for the initial fetch. A verified cache supports subsequent
  offline builds.

Release generation also fails closed unless CPython's embedded SQLite and
zlib runtimes and the byte-affecting Python packages match the pinned build
identity: SQLite 3.50.4 (including its source ID and compile-options digest),
zlib 1.2.12, Jinja2 3.1.6, MarkupSafe 3.0.3, markdown-it-py 3.0.0, and mdurl
0.1.2.

From `docsets/Arm_C_Language_Extensions`, install the locked environment and
run the explicit fetch, conversion, and verification stages:

```bash
uv sync --locked --project generator --extra test

uv run --frozen --project generator python generate_docset.py fetch

uv run --frozen --project generator python generate_docset.py build \
  --clang-tblgen /opt/homebrew/opt/llvm/bin/clang-tblgen \
  --llvm-mca /opt/homebrew/opt/llvm/bin/llvm-mca \
  --llvm-mc /opt/homebrew/opt/llvm/bin/llvm-mc \
  --output-dir .

uv run --frozen --project generator python generate_docset.py verify \
  --output-dir .
```

The fetch stage writes to the private per-user cache at
`~/.arm-acle-docset-cache` and verifies every network input against its manifest
SHA-256. Pass `--cache-dir` only when an explicit private cache location is
needed. The cache root is current-user-owned and kept at mode `0700`; symlinked,
special-file, untrusted-owner, and unsafely writable path layouts are rejected.
The build hashes and copies each already-opened source file into a sealed
private snapshot and consumes only that snapshot. This protects against
other-UID replacement and ordinary concurrent cache updates; a malicious
same-UID process is outside the isolation claim.

The build regenerates and verifies the six public LLVM Arm headers, then runs
all six fixed performance profiles before normalization. All three LLVM tools
must report 22.1.1. The build records the observed SHA-256 of every resolved
executable and its normalized complete `--version` output, then re-probes each
tool after use; identity drift aborts the build. The recorded LLVM release tag
and source revision are declared provenance, not cryptographic proof of how an
arbitrary binary was built.

Use repeatable `--performance-profile CPU` options only when deliberately
building a proper subset for development, and pair them with `--no-archive`.
A release build omits both options and produces the canonical ordered set of
all six profiles. A development subset removes any stale release archive and
is accepted by verification only with `--allow-development-subset`. Explicitly
selecting all six profiles is rejected; omit `--performance-profile` for a
release.

A full release build produces:

```text
Arm_C_Language_Extensions.docset
Arm_C_Language_Extensions.tgz
```

The bundle records its release inputs in
`Contents/Resources/build-manifest.json`. The schema binds the exact generator
entry point, lock and project files, Python sources, templates, icons, notices,
licenses, complete source lock, build-runtime identity, release/subset mode,
ordered CPU profiles, and the three LLVM tool identities observed during the
build. Normal verification rehashes the current build inputs, source lock, and
runtime; it does not need access to the original LLVM executables. It also
regenerates the canonical archive and compares its byte digest, member order,
types, metadata, sizes, and hashes with the current bundle, so a missing, stale,
or substituted `.tgz` fails verification.

To prove that a populated source directory is sufficient without network
access, pass it to the build explicitly:

```bash
uv run --frozen --project generator python generate_docset.py build \
  --source-dir /path/to/verified/arm-acle-sources \
  --offline \
  --clang-tblgen /path/to/llvm-22.1.1/bin/clang-tblgen \
  --llvm-mca /path/to/llvm-22.1.1/bin/llvm-mca \
  --llvm-mc /path/to/llvm-22.1.1/bin/llvm-mc \
  --output-dir .
```

The generated HTML, styles, notices, and licenses are static and self-contained.
Installed reference pages do not require JavaScript or network access. The
archive contains only the `.docset` bundle; generator code, the verified source
cache, GCC validation inputs, and test fixtures remain outside it.

## Licensing and attribution

The specification material adapted from ACLE's `main/`, `neon_intrinsics/`,
and `mve_intrinsics/` trees is licensed under Creative Commons
Attribution-ShareAlike 4.0 International together with Arm's accompanying
patent-license grant. The `tools/intrinsic_db/` tables consumed by the converter
are licensed under Apache-2.0. LLVM-derived declaration and scheduling-model
data is licensed under Apache-2.0 WITH LLVM-exception.
The Arm A-profile feature registry remains subject to its Arm Proprietary
Notice. The generator retains only factual minimum-version and dependency
relationships with page-level citations; it does not redistribute the source
document or copy its prose, tables, or images.
GCC 16.2.0 option pages are licensed under
GFDL-1.3-invariants-or-later; the generated pages retain factual option
spellings and citations without copying GCC manual prose.

For the portions of generated pages that adapt CC BY-SA ACLE specification
material, CC BY-SA 4.0 is the Adapter's License for the new copyrightable
expression introduced by this docset. This statement does not relicense the
generator source or material represented under the Apache, LLVM, GFDL, or Arm
Proprietary terms described above; this contribution makes no separate license
declaration for the generator source. The upstream material remains subject to
its original license and Arm's accompanying patent grant. The generated pages
are modified works: the converter normalizes presentation, merges source-backed
fields, expands concrete declarations, creates search metadata and cross-links,
and adds provenance and diagnostics. It does not use the Arm corporate logo.
GCC source and tests are consulted only during a transient static sampled
cross-check and are not redistributed; this does not claim to compile the
samples with GCC.

See [NOTICE.md](NOTICE.md) and [LICENSES](LICENSES/) for the complete source,
change, trademark, and license notices distributed with this contribution.

## Bugs and updates

Please report missing entries, incorrect signatures or requirements, broken
offline links, or source mismatches through this repository's issue tracker.
Updates should change the source manifest pins and hashes, regenerate the full
archive, review the catalog/provenance diff, run the converter tests, and verify
the resulting Dash archive before submission.
