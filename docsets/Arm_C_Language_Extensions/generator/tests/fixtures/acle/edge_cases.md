# Helper intrinsics

```
fpm_t __arm_fpm_init(void);
uint64_t __unnamed_parameters(uint64_t, unsigned int);
```

Returns a default mode value.

## Example

``` c
svint8_t svexample_fake(svint8_t value);
```

## Unsupported variants

``` c
// And similarly for unsigned forms.
svint32_t svsample[_s32](svint32_t value);
```
