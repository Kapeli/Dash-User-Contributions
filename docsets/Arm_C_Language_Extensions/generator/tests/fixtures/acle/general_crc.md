# About this document

## Support levels

All content in this document is at the **Release** quality level,
unless a different support level is specified in the text.

# Data-processing intrinsics

## CRC32 intrinsics

CRC32 intrinsics provide access to the CRC32 instructions introduced in
Armv8-A for the AArch32 and AArch64 execution states. The intrinsics are
available when `__ARM_FEATURE_CRC32` is defined.

``` c
uint32_t __crc32b(uint32_t accumulator, uint8_t value);
```

Performs a CRC-32 checksum from one byte.

``` c
uint32_t __crc32d(uint32_t accumulator, uint64_t value);
```

Performs a CRC-32 checksum from one double word.

To access these intrinsics, `<arm_acle.h>` should be included.
