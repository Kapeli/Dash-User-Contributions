# About this document

## Support levels

All content in this document is at the **Release** quality level,
unless a different support level is specified in the text.

# SVE language extensions and intrinsics

## SVE2.3 lookup table

The specification for this section is in [**Alpha** state](#support-levels)
and might change. The intrinsics are defined by the header file
[`<arm_sve.h>`](#arm_sve.h) when `__ARM_FEATURE_SVE2p3` is defined to 1.

#### LUTI6

Lookup table read with 6-bit indices.

``` c
// Variants are also available for: _u8 and _mf8.
svint8_t svluti6[_s8_x2](svint8x2_t table, svuint8_t indices);
```

### Mapping of SVE instructions to intrinsics

#### List of instructions

| **Instruction** | **Intrinsic** |
| --------------- | ------------- |
| ADD (vectors) | [`svadd`](https://example.invalid/?q=svadd) |
| ASRR | [`svasr`](https://example.invalid/?q=svasr) (optimization of `_x` forms) |

# SME language extensions and intrinsics

The specification for SME is in [**Beta** state](#support-levels) and might
change or be extended in the future.

## SME functions and intrinsics

### SME PSTATE functions

#### Prototypes

``` c
bool __arm_has_sme(void) __arm_streaming_compatible;

// Function with external linkage.
void __arm_za_disable(void) __arm_streaming_compatible;
```

#### Semantics

**`__arm_has_sme()`**

> Returns true if the current thread has access to SME.

**`__arm_za_disable()`**

> Commits any pending lazy save and turns ZA off.

### SME instruction intrinsics

#### BFMOPA, FMOPA

Floating-point outer product.

``` c
void svmopa_za32[_f32]_m(svbool_t pn, svbool_t pm, svfloat32_t zn,
                          svfloat32_t zm)
  __arm_streaming __arm_inout("za") __arm_preserves("zt0");
```

### SVE2.1 and SME2 instruction intrinsics

The functions in this section are defined by either the header file
[`<arm_sve.h>`](#arm_sve.h) or [`<arm_sme.h>`](#arm_sme.h)
when `__ARM_FEATURE_SVE2p1` or `__ARM_FEATURE_SME2` is defined, respectively.
They can only be called from non-streaming code if
`__ARM_FEATURE_SVE2p1` is defined. They can only be called from streaming code
if `__ARM_FEATURE_SME2` is defined.

#### UCLAMP, SCLAMP

``` c
svint32_t svclamp[_s32](svint32_t value, svint32_t minimum,
                         svint32_t maximum);
```
