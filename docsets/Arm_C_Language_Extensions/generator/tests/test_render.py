from __future__ import annotations

from dataclasses import replace
from html.parser import HTMLParser
from pathlib import Path

from arm_acle_docset.model import (
    Alias,
    AvailabilityExpr,
    AvailabilityOp,
    CallableKind,
    CompilationRequirements,
    CompilerFlagExample,
    ConcreteCallable,
    Constraint,
    ConstraintKind,
    Diagnostic,
    DiagnosticSeverity,
    FieldProvenance,
    InstructionMapping,
    InstructionRelationKind,
    Maturity,
    ModeAvailability,
    NameRole,
    NumericRange,
    Parameter,
    ParameterDocumentation,
    PerformanceConfidence,
    PerformanceEvidenceKind,
    PerformanceMetric,
    PerformanceRecord,
    Provenance,
    ProvenanceKind,
    Semantics,
    Signature,
    SourceRef,
    StateAccess,
    StateAccessMode,
)
from arm_acle_docset.pipeline import _attach_feature_flags
from arm_acle_docset.render import DashRenderer, IndexEntry
from arm_acle_docset.sources.feature_flags import (
    DEFAULT_FEATURE_FLAG_MANIFEST,
    index_feature_flags_by_macro,
)


SOURCE_COMMIT = "62d9cbd68abb6d18dd8f06980da7758d9dbe0560"


class HrefCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        self.hrefs.extend(
            value for name, value in attrs if name == "href" and value is not None
        )


def rendered_hrefs(html: str) -> tuple[str, ...]:
    collector = HrefCollector()
    collector.feed(html)
    return tuple(collector.hrefs)


def source_ref() -> SourceRef:
    return SourceRef(
        id="acle-crc",
        repository="ARM-software/acle",
        commit=SOURCE_COMMIT,
        path="main/acle.md",
        start_line=4200,
        end_line=4230,
        license_id="CC-BY-SA-4.0 AND Apache-Patent-License",
    )


def explicit_provenance() -> Provenance:
    return Provenance(ProvenanceKind.EXPLICIT, sources=(source_ref(),))


def crc_callable(*, name: str = "__crc32b") -> ConcreteCallable:
    provenance = explicit_provenance()
    operand_constraint = Constraint(
        ConstraintKind.RANGE,
        "The byte operand is interpreted as an unsigned 8-bit value.",
        parameter="data",
        provenance=provenance,
    )
    return ConcreteCallable(
        family="General ACLE / CRC",
        name=name,
        signature=Signature(
            return_type="uint32_t",
            parameters=(
                Parameter("accumulator", "uint32_t"),
                Parameter("data", "uint8_t", constraints=(operand_constraint,)),
            ),
            raw=f"uint32_t {name}(uint32_t accumulator, uint8_t data)",
        ),
        kind=CallableKind.INTRINSIC,
        aliases=(
            Alias(
                f"{name}_alias",
                NameRole.ALTERNATE,
                provenance=Provenance(
                    ProvenanceKind.EXPANDED,
                    sources=(source_ref(),),
                    rule="documented-alias",
                ),
            ),
        ),
        availability=AvailabilityExpr.all(
            AvailabilityExpr.defined("__ARM_FEATURE_CRC32"),
            AvailabilityExpr.raw("AArch64 or an implementation with the CRC extension"),
        ),
        maturity=Maturity.RELEASE,
        semantics=Semantics(
            summary="Updates a CRC-32C accumulator with one byte.",
            description="The operation uses the Castagnoli polynomial.\n\nIt is not a memory access.",
            operation="result = CRC32C(accumulator, data)",
            result="The updated CRC-32C accumulator.",
            parameters=(
                ParameterDocumentation(
                    "accumulator", "The input CRC accumulator.", provenance
                ),
                ParameterDocumentation("data", "The byte to fold in.", provenance),
            ),
            constraints=(operand_constraint,),
            notes=("Compiler lowering can vary with optimization settings.",),
            provenance=provenance,
        ),
        instructions=(
            InstructionMapping(
                InstructionRelationKind.SEMANTIC_EQUIVALENT,
                mnemonic="CRC32CB",
                instruction_set="A64",
                form="Wd, Wn, Wm",
                argument_mapping="accumulator -> Wn; data -> Wm",
                result_mapping="Wd -> result",
                guaranteed_emission=False,
                provenance=provenance,
            ),
        ),
        state_access=(
            StateAccess("condition flags", StateAccessMode.PRESERVES, provenance),
        ),
        compilation=CompilationRequirements(
            architecture_min="Armv8-A",
            profiles=("A-profile",),
            extensions=("+crc",),
            feature_macros=("__ARM_FEATURE_CRC32",),
            headers=("arm_acle.h",),
            execution_states=("AArch64",),
            compiler_flags=(
                CompilerFlagExample(
                    "Clang",
                    version="18 or newer",
                    base_march="armv8-a",
                    flags=("-march=armv8-a+crc",),
                    default_enabled=False,
                    notes=("Example for an AArch64 compilation target.",),
                    provenance=provenance,
                    availability=AvailabilityExpr.defined("__ARM_FEATURE_CRC32"),
                    mode="non_streaming",
                    target="aarch64",
                ),
            ),
            availability=AvailabilityExpr.defined("__ARM_FEATURE_CRC32"),
            availability_by_mode=(
                ModeAvailability(
                    "non-streaming",
                    AvailabilityExpr.defined("__ARM_FEATURE_CRC32"),
                    provenance,
                ),
            ),
            provenance=provenance,
        ),
        performance=(
            PerformanceRecord(
                microarchitecture="Example Cortex core",
                cpu="example-cpu",
                instruction_form="CRC32CB Wd, Wn, Wm",
                latency=PerformanceMetric(
                    NumericRange(2), provenance, PerformanceConfidence.HIGH
                ),
                reciprocal_throughput=PerformanceMetric(
                    NumericRange(1, unit="cycles/instruction"),
                    provenance,
                    PerformanceConfidence.HIGH,
                ),
                uops=PerformanceMetric(
                    NumericRange(1, unit="µops"),
                    provenance,
                    PerformanceConfidence.MEDIUM,
                ),
                resources=("integer execution pipe",),
                resources_provenance=provenance,
                evidence_kind=PerformanceEvidenceKind.OFFICIAL,
                provenance=provenance,
                confidence=PerformanceConfidence.HIGH,
                notes=("Example pinned performance record.",),
            ),
        ),
        headers=("arm_acle.h",),
        taxonomy=(("General intrinsics", "CRC"),),
        related=("__crc32h", "__crc32w"),
        sources=(source_ref(),),
        field_provenance=(
            FieldProvenance("semantics", provenance),
            FieldProvenance(
                "aliases",
                Provenance(
                    ProvenanceKind.EXPANDED,
                    sources=(source_ref(),),
                    rule="documented-alias",
                ),
            ),
        ),
        diagnostics=(
            Diagnostic(
                "render.example",
                "This synthetic record exercises visible diagnostics.",
                DiagnosticSeverity.INFO,
                sources=(source_ref(),),
            ),
        ),
    )


def unresolved_callable() -> ConcreteCallable:
    return ConcreteCallable(
        family="SVE",
        name="svunresolved_z",
        signature=Signature("svint32_t", (Parameter("pg", "svbool_t"),)),
        maturity=Maturity.ALPHA,
        compilation=CompilationRequirements(
            availability=AvailabilityExpr.defined("__ARM_FEATURE_SVE"),
            unresolved_reason=(
                "The pinned section does not provide a compiler flag example for "
                "this callable."
            ),
        ),
        diagnostics=(
            Diagnostic(
                "instruction.unresolved",
                "The pinned sources do not provide a callable-to-instruction mapping.",
                DiagnosticSeverity.WARNING,
            ),
        ),
    )


def test_render_callable_uses_uniform_dash_layout_and_indexes_aliases() -> None:
    page = DashRenderer().render_callable(crc_callable())

    assert page.relative_path.startswith("intrinsics/")
    assert page.relative_path.endswith(".html")
    assert set(page.index_entries) == {
        IndexEntry("__crc32b", "Function", page.relative_path),
        IndexEntry("CRC32CB", "Instruction", page.relative_path),
    }
    for heading in (
        "Compilation requirements",
        "Parameters",
        "Semantics",
        "Result",
        "Instruction mapping",
        "Performance",
        "Constraints",
        "Aliases",
        "Related intrinsics",
        "Source",
    ):
        assert f">{heading}<" in page.html
    assert page.html.index('id="compilation-requirements"') < page.html.index(
        'id="source"'
    )

    assert "//apple_ref/cpp/Function/__crc32b" in page.html
    assert "//apple_ref/cpp/Instruction/CRC32CB" in page.html
    assert "maturity-release" in page.html
    assert "+crc" in page.html
    assert "AArch64" in page.html
    assert "Availability by calling mode" in page.html
    assert "Non-Streaming" in page.html
    assert "-march=armv8-a+crc" in page.html
    assert "aarch64 · Non Streaming" in page.html
    assert "defined(__ARM_FEATURE_CRC32)" in page.html
    assert "Not guaranteed" in page.html
    assert "different equivalent sequence" in page.html
    assert "Example Cortex core" in page.html
    assert "2 cycles" in page.html
    assert 'class="performance-table"' in page.html
    assert "Full provenance" in page.html
    assert "Example pinned performance record." in page.html
    assert SOURCE_COMMIT in page.html
    assert "CC-BY-SA-4.0 AND Apache-Patent-License" in page.html
    assert "Field provenance" in page.html


def test_render_type_uses_dash_type_index_and_exact_declaration() -> None:
    provenance = explicit_provenance()
    type_page = ConcreteCallable(
        family="mve",
        name="int32x4_t",
        signature=Signature(
            "typedef __attribute__((neon_vector_type(4))) int32_t int32x4_t;",
            raw="typedef __attribute__((neon_vector_type(4))) int32_t int32x4_t;",
        ),
        kind=CallableKind.TYPE,
        semantics=Semantics(summary="Public ACLE data type declaration."),
        compilation=CompilationRequirements(
            headers=("arm_neon.h",), provenance=provenance
        ),
        sources=(source_ref(),),
    )

    page = DashRenderer().render_callable(type_page)

    assert page.index_entries == (IndexEntry("int32x4_t", "Type", page.relative_path),)
    assert "//apple_ref/cpp/Type/int32x4_t" in page.html
    assert "typedef __attribute__((neon_vector_type(4))) int32_t int32x4_t;" in page.html
    assert ">Compilation requirements<" in page.html
    assert ">Semantics<" in page.html
    assert ">Source<" in page.html
    assert page.html.index('id="compilation-requirements"') < page.html.index(
        'id="source"'
    )
    assert ">Parameters<" not in page.html
    assert ">Performance<" not in page.html
    assert '<link rel="stylesheet" href="../assets/style.css">' in page.html
    assert "<script" not in page.html
    assert 'src="http' not in page.html


def test_render_type_properties_and_links_type_references(tmp_path: Path) -> None:
    def type_record(name: str) -> ConcreteCallable:
        return ConcreteCallable(
            family="neon",
            name=name,
            signature=Signature(f"typedef int {name};", raw=f"typedef int {name};"),
            kind=CallableKind.TYPE,
            semantics=Semantics(summary="Public ACLE data type declaration."),
            compilation=CompilationRequirements(headers=("arm_neon.h",)),
            sources=(source_ref(),),
        )

    int32x4 = type_record("int32x4_t")
    float32x4 = type_record("float32x4_t")
    conversion = ConcreteCallable(
        family="mve",
        name="vcvtq_s32_f32",
        signature=Signature(
            "int32x4_t", (Parameter("value", "float32x4_t"),)
        ),
        semantics=Semantics(summary="Converts lanes."),
        taxonomy=(("Vector arithmetic", "Add", "Addition"),),
        sources=(source_ref(),),
    )
    reinterpret = ConcreteCallable(
        family="neon",
        name="vreinterpretq_s32_f32",
        signature=Signature(
            "int32x4_t", (Parameter("value", "float32x4_t"),)
        ),
        semantics=Semantics(summary="Reinterprets lanes."),
        sources=(source_ref(),),
    )
    non_cast_internal = ConcreteCallable(
        family="neon",
        name="__arm_vreinterpretq_s32_f32",
        signature=Signature(
            "int32x4_t", (Parameter("value", "float32x4_t"),)
        ),
        semantics=Semantics(summary="Not a public cast entry point."),
        sources=(source_ref(),),
    )
    construction = ConcreteCallable(
        family="neon",
        name="vdupq_n_s32",
        signature=Signature("int32x4_t", (Parameter("value", "int32_t"),)),
        semantics=Semantics(summary="Duplicates a scalar value."),
        sources=(source_ref(),),
    )
    extraction = ConcreteCallable(
        family="neon",
        name="vgetq_lane_s32",
        signature=Signature(
            "int32_t",
            (Parameter("value", "int32x4_t"), Parameter("lane", "int")),
        ),
        semantics=Semantics(summary="Extracts one lane."),
        sources=(source_ref(),),
    )

    pages = DashRenderer().render_to_directory(
        (
            int32x4,
            float32x4,
            conversion,
            reinterpret,
            non_cast_internal,
            construction,
            extraction,
        ),
        tmp_path,
    )
    html_by_path = {page.relative_path: page.html for page in pages}
    type_html = html_by_path[f"intrinsics/{int32x4.slug}.html"]
    function_html = html_by_path[f"intrinsics/{conversion.slug}.html"]

    assert "Type properties" in type_html
    assert "128 bits (4 × 32-bit lanes)" in type_html
    assert "Value-conversion functions" in type_html
    assert "Same-width reinterpret casts" in type_html
    assert "Build or insert from scalar values" in type_html
    assert "Extract a scalar value" in type_html
    assert "Functions returning this type" in type_html
    assert "Functions accepting this type as an operand" in type_html
    assert "128-bit data types" in type_html
    assert f'href="{float32x4.slug}.html"' in type_html
    assert f'href="{conversion.slug}.html"' in type_html
    assert f'href="{reinterpret.slug}.html"' in type_html
    assert f'href="{construction.slug}.html"' in type_html
    assert f'href="{extraction.slug}.html"' in type_html
    assert non_cast_internal.name not in type_html.split(
        "Same-width reinterpret casts", maxsplit=1
    )[1].split("Build or insert from scalar values", maxsplit=1)[0]
    assert f'href="{int32x4.slug}.html"' in function_html
    assert f'href="{float32x4.slug}.html"' in function_html
    assert "<strong>Type:</strong>" in function_html
    assert 'Intrinsic · <a href="category-mve-' in function_html
    assert ">MVE</a> / <a href=" in function_html
    assert 'class="tag-list"' not in function_html
    root_category = next(
        page
        for page in pages
        if page.index_entries and page.index_entries[0].name == "ACLE · MVE"
    )
    vector_category = next(
        page
        for page in pages
        if page.index_entries
        and page.index_entries[0].name == "ACLE · MVE / Vector arithmetic"
    )
    category = next(
        page
        for page in pages
        if page.index_entries
        and page.index_entries[0].name == "ACLE · MVE / Vector arithmetic / Add"
    )
    assert "Vector arithmetic" in root_category.html
    assert "Add" in vector_category.html
    assert "Subcategories" in category.html
    assert "Addition" in category.html


def test_render_callable_marks_missing_evidence_instead_of_fabricating_values() -> None:
    page = DashRenderer().render_callable(unresolved_callable())

    assert "maturity-alpha" in page.html
    assert "The pinned section does not provide a compiler flag example" in page.html
    assert (
        "The pinned sources do not provide a callable-to-instruction mapping"
        in page.html
    )
    assert "No public, source-pinned microarchitecture data is available" in page.html
    assert "No source-backed result description is available" in page.html
    assert (
        "No source reference was attached. This is a release-blocking data issue."
        in page.html
    )


def test_render_callable_shows_partial_feature_mapping_alongside_existing_flags() -> (
    None
):
    callable_ = crc_callable()
    reason = (
        "Partial feature-to-compiler mapping: "
        "__ARM_FEATURE_EXAMPLE: no aarch64 compiler context is pinned"
    )
    page = DashRenderer().render_callable(
        replace(
            callable_,
            compilation=replace(
                callable_.compilation,
                feature_macros=(
                    *callable_.compilation.feature_macros,
                    "__ARM_FEATURE_EXAMPLE",
                ),
                unresolved_reason=reason,
            ),
        )
    )

    assert "-march=armv8-a+crc" in page.html
    assert reason in page.html


def test_render_streaming_only_flags_do_not_show_global_calling_mode() -> None:
    gate = AvailabilityExpr.defined("__ARM_FEATURE_SME")
    provenance = explicit_provenance()
    callable_ = ConcreteCallable(
        family="sme",
        name="svstreaming_synthetic",
        signature=Signature(
            "svfloat16x2_t",
            (
                Parameter("zdn", "svfloat16x2_t"),
                Parameter("zm", "svfloat16x2_t"),
            ),
            attributes=("__arm_streaming",),
        ),
        availability=gate,
        compilation=CompilationRequirements(
            feature_macros=("__ARM_FEATURE_SME",),
            availability=gate,
            availability_by_mode=(ModeAvailability("streaming", gate, provenance),),
            provenance=provenance,
        ),
    )
    callable_ = _attach_feature_flags(
        callable_,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )

    assert len(callable_.compilation.compiler_flags) == 4
    page = DashRenderer().render_callable(callable_)
    assert "All applicable calling modes" not in page.html
    assert "aarch64 · Streaming" in page.html


def test_render_global_calling_context_labels_streaming_flags() -> None:
    gate = AvailabilityExpr.defined("__ARM_FEATURE_SME")
    availability = AvailabilityExpr.all(
        gate,
        AvailabilityExpr(
            AvailabilityOp.CALLING_CONTEXT,
            value=("streaming",),
        ),
    )
    callable_ = ConcreteCallable(
        family="sme",
        name="svstreaming_from_global_availability",
        signature=Signature("void", attributes=("__arm_streaming",)),
        availability=availability,
        compilation=CompilationRequirements(
            feature_macros=("__ARM_FEATURE_SME",),
            provenance=explicit_provenance(),
        ),
    )

    callable_ = _attach_feature_flags(
        callable_,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )

    assert len(callable_.compilation.compiler_flags) == 4
    assert {example.mode for example in callable_.compilation.compiler_flags} == {
        "streaming"
    }
    page = DashRenderer().render_callable(callable_)
    assert "All applicable calling modes" not in page.html
    assert "aarch64 · Streaming" in page.html


def test_render_callable_does_not_repeat_compiler_model_note_in_metric_cells() -> None:
    callable_ = crc_callable()
    record = callable_.performance[0]
    metric_note = "LLVM scheduling model estimate; not measured hardware behavior."
    compiler_model_record = replace(
        record,
        evidence_kind=PerformanceEvidenceKind.COMPILER_MODEL,
        latency=replace(record.latency, notes=(metric_note,)),
        reciprocal_throughput=replace(
            record.reciprocal_throughput, notes=(metric_note,)
        ),
        uops=replace(record.uops, notes=(metric_note,)),
    )

    page = DashRenderer().render_callable(
        replace(callable_, performance=(compiler_model_record,))
    )

    assert "<td>2 cycles</td>" in page.html
    assert "<td>1 cycles/instruction</td>" in page.html
    assert "µops: 1 µops; resources:" in page.html
    assert metric_note not in page.html
    assert (
        page.html.count("LLVM scheduling-model estimate; not measured hardware data.")
        == 1
    )
    assert "0 cycles" not in page.html


def test_render_callable_explains_partial_performance_cells() -> None:
    provenance = explicit_provenance()
    unresolved = Provenance.unresolved(
        "The pinned performance table does not report this metric."
    )
    record = PerformanceRecord(
        microarchitecture="Example core",
        latency=PerformanceMetric(
            NumericRange(3), provenance, PerformanceConfidence.HIGH
        ),
        reciprocal_throughput=PerformanceMetric(provenance=unresolved),
        uops=PerformanceMetric(provenance=unresolved),
        resources_provenance=unresolved,
        evidence_kind=PerformanceEvidenceKind.OFFICIAL,
        provenance=provenance,
        confidence=PerformanceConfidence.MEDIUM,
    )
    page = DashRenderer().render_callable(
        replace(crc_callable(), performance=(record,))
    )

    assert "3 cycles" in page.html
    assert (
        "Unavailable — The pinned performance table does not report this metric."
        in page.html
    )
    assert (
        "resources: unavailable — The pinned performance table does not report this metric."
        in page.html
    )


def test_rendering_escapes_source_text() -> None:
    callable_ = crc_callable(name="unsafe_name")
    callable_ = ConcreteCallable(
        family=callable_.family,
        name=callable_.name,
        signature=callable_.signature,
        semantics=Semantics(
            description='<script src="https://example.test/x.js"></script>'
        ),
    )

    page = DashRenderer().render_callable(callable_)

    assert "&lt;script" in page.html
    assert '<script src="https://example.test/x.js">' not in page.html


def test_render_callable_unlinks_fragment_only_markdown_references() -> None:
    callable_ = crc_callable()
    description = (
        "Read [*local details*](#local-details) and "
        "[**external reference**](https://example.test/spec#external-details)."
    )
    page = DashRenderer().render_callable(
        replace(
            callable_,
            semantics=replace(callable_.semantics, description=description),
        )
    )

    hrefs = rendered_hrefs(page.html)
    assert not any(href.startswith("#") for href in hrefs)
    assert "https://example.test/spec#external-details" in hrefs
    assert "Read <em>local details</em> and" in page.html
    assert (
        '<a href="https://example.test/spec#external-details">'
        "<strong>external reference</strong></a>"
    ) in page.html


def test_render_index_includes_catalog_level_diagnostics() -> None:
    page = DashRenderer().render_index(
        (crc_callable(),),
        catalog_diagnostics=(
            Diagnostic(
                "pipeline.example",
                "This synthetic catalog diagnostic exercises the landing summary.",
                DiagnosticSeverity.WARNING,
            ),
        ),
    )

    assert "<td>Warning</td><td>1</td>" in page.html
    assert "Diagnostic entries" in page.html
    assert "not affected callables" in page.html


def test_render_to_directory_is_deterministic_and_writes_offline_landing(
    tmp_path: Path,
) -> None:
    renderer = DashRenderer()
    first = tmp_path / "first"
    second = tmp_path / "second"
    callables = (unresolved_callable(), crc_callable())

    first_pages = renderer.render_to_directory(
        callables,
        first,
        version="62d9cbd68abb",
        source_revision=SOURCE_COMMIT,
    )
    second_pages = renderer.render_to_directory(
        reversed(callables),
        second,
        version="62d9cbd68abb",
        source_revision=SOURCE_COMMIT,
    )

    assert [page.relative_path for page in first_pages] == [
        page.relative_path for page in second_pages
    ]
    first_files = sorted(
        path.relative_to(first) for path in first.rglob("*") if path.is_file()
    )
    second_files = sorted(
        path.relative_to(second) for path in second.rglob("*") if path.is_file()
    )
    assert first_files == second_files
    for relative_path in first_files:
        assert (first / relative_path).read_bytes() == (
            second / relative_path
        ).read_bytes()

    landing = (first / "index.html").read_text(encoding="utf-8")
    assert "Concrete callables" in landing
    assert "Release: 1" in landing
    assert "Alpha: 1" in landing
    assert SOURCE_COMMIT in landing
    assert "CC BY-SA 4.0" in landing
    assert "Installed runtime dependencies" in landing
    assert "<title>Overview</title>" in landing
    assert "<script" not in landing
    assert (first / "assets" / "style.css").is_file()
