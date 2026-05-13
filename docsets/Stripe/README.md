Stripe Dash Docset
==================

- __Docset Description__:
  - Offline Dash docset for Stripe's English developer documentation.

- __Author__:
  - [weishen612](https://github.com/weishen612), prepared for [Kapeli/Dash-User-Contributions#2014](https://github.com/Kapeli/Dash-User-Contributions/issues/2014).

- __Upstream docs__:
  - [https://docs.stripe.com/](https://docs.stripe.com/)
  - [https://docs.stripe.com/llms.txt](https://docs.stripe.com/llms.txt)

- __Prerequisites__:
  - Python 3.11 or newer.
  - Network access to `docs.stripe.com` when building from upstream.

- __How the docset was generated__:
  - Read Stripe's public `llms.txt` index.
  - Download only the public Markdown pages linked from that index.
  - Convert the Markdown pages into static offline HTML.
  - Build a Dash search index from the page titles and headings.
  - Package the result as `Stripe.docset` and archive it into `Stripe.tgz`.

Example command:

```bash
python3 generate_stripe_docset.py --delay 0.2
```

To force a fresh download instead of reusing the local Markdown cache:

```bash
python3 generate_stripe_docset.py --refresh-cache --delay 0.2
```

If your network requires an explicit proxy, set the standard proxy environment variables before running the generator:

```bash
HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897 python3 generate_stripe_docset.py --delay 0.2
```

For a quick smoke build, limit the number of downloaded pages:

```bash
python3 generate_stripe_docset.py --max-pages 25 --delay 0.2
```

Generated artifacts:

```text
Stripe.docset
Stripe.tgz
Stripe.tgz.sha256
icon.png
icon@2x.png
```

- __Known limitations__:
  - The generator intentionally uses Stripe's Markdown endpoints instead of mirroring the dynamic docs website, so interactive examples and account-specific Dashboard content remain online-only.
  - Links that leave `docs.stripe.com` remain external.
  - The Markdown renderer is conservative and optimized for readable offline reference pages rather than pixel-perfect reproduction of Stripe's website.
