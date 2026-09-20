# Janet docset

Hi, I’m [David Gouch][dg] and this is a documentation docset for [Janet][]. The source code is available on [GitHub][].

[dg]: https://davidgouch.com
[janet]: https://janet-lang.org
[github]: https://github.com/gouch/janet-docset

![Dash screenshot](./screenshot.png)

## Build instructions

Build dependencies are `janet`, `tar` and `wget`.

A macOS shell environment is assumed. Linux might work too.

To fetch documentation and generate a docset, run:

```shell
janet build.janet
```

Or to generate a docset from the bundled mirror, run:

```shell
janet build.janet --stable
```

This will create two assets:
- `dist/` contains the format for [Dash-User-Contributions][contrib].
- `tmp/Janet.docset` is a package that can be added to your docset app. For Dash, move it somewhere stable (Dash will import it by reference) then double-click. For Zeal, move it to your docset storage directory.

[contrib]: https://github.com/Kapeli/Dash-User-Contributions
