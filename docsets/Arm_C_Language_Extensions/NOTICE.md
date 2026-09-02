# Third-Party Notices

This notice applies to the generated **Arm C Language Extensions** Dash docset
and its generator. The docset is an unofficial adaptation maintained by Joey
Teng. It is not produced, sponsored, or endorsed by Arm.

## Arm C Language Extensions

The docset adapts material from the Arm C Language Extensions repository at
commit `62d9cbd68abb6d18dd8f06980da7758d9dbe0560`:

<https://github.com/ARM-software/acle/tree/62d9cbd68abb6d18dd8f06980da7758d9dbe0560>

Copyright notices in the pinned source identify Arm Limited and/or its
affiliates, Google LLC (`Copyright 2022 Google LLC.`), and Matt P. Dziubinski
(`Copyright 2021 Matt P. Dziubinski <matdzb@gmail.com>`).
The consumed Advanced SIMD and MVE classification tables also state:
`Classification provided by Chris Walsh @ Arm.`

- Specification material from `main/`, `neon_intrinsics/`, and
  `mve_intrinsics/` is licensed under Creative Commons
  Attribution-ShareAlike 4.0 International together with Arm's accompanying
  patent-license grant. See `LICENSES/ARM-ACLE-SPECIFICATION.md` and
  `LICENSES/CC-BY-SA-4.0.txt`.
- Machine-readable intrinsic data from `tools/intrinsic_db/` is licensed under
  Apache License 2.0. See `LICENSES/ARM-ACLE-TOOLS.md`.

This docset changes the upstream presentation by normalizing heterogeneous
sources into one static API layout, joining source-backed fields, expanding
concrete callable declarations, generating Dash search metadata and cross-links,
and adding explicit provenance, maturity labels, diagnostics, compilation
examples, and model-specific performance evidence. Entries identify their
upstream source and revision. Unresolved facts are labeled rather than inferred.
For the portions of generated pages that constitute adapted CC BY-SA ACLE
specification material, CC BY-SA 4.0 is the Adapter's License for the new
copyrightable expression introduced by this docset. This statement does not
relicense the generator source or material represented under other terms; this
contribution makes no separate license declaration for the generator source.
The upstream material remains subject to its original license and accompanying
patent grant.

## Arm A-profile feature registry

Minimum-architecture and ISA-dependency facts are cited from *Feature names in
A-profile architecture*, document ID `109697_2025_12_en`, version 1.0, issue
2025_12 (12 December 2025):

<https://documentation-service.arm.com/static/69402e206efc1635355c3bb2?token=>

The source document remains subject to its Arm Proprietary Notice. The
generator records only the factual minimum-version and dependency relationships
needed by feature mappings, together with page-level source references. Its
prose, tables, images, and PDF are not copied into or distributed with the
docset, archive, or source cache.

## LLVM Project

Public declaration data, compiler-feature mappings, and scheduling-model data
are derived from LLVM `llvmorg-22.1.1`, peeled to commit
`fef02d48c08db859ef83f84232ed78bd9d1c323a`:

<https://github.com/llvm/llvm-project/tree/fef02d48c08db859ef83f84232ed78bd9d1c323a>

LLVM is licensed under Apache License 2.0 with LLVM Exceptions. See
`LICENSES/LLVM.txt`. Any latency, reciprocal-throughput, micro-op, or resource
value attributed to LLVM is a compiler scheduling-model estimate, not a
physical-hardware measurement.

## GCC

GCC 16.2.0 manuals are cited for compiler-option spellings. A fixed GCC source
revision, `fcfb06e236d4d1689a6caf8e5409b078262af481`, is used only for a transient
static sampled cross-check; the generator does not claim to compile those
samples with GCC. GCC source, tests, and documentation text are not copied
into the generated docset or archive. The cited manual is licensed under
GFDL-1.3-invariants-or-later; generated pages retain factual option spellings
and source links without redistributing GCC manual prose.

## Trademarks

Arm, Neon, SVE, SME, Helium, and related names may be registered trademarks or
trademarks of Arm Limited (or its subsidiaries) in the United States and/or
elsewhere. All rights reserved by their respective owners. The contribution
uses those names only to identify the documented interfaces, uses an original
neutral icon, and does not use the Arm corporate logo. Arm's upstream notice is
preserved in `LICENSES/ARM-TRADEMARK-NOTICE.md`.
