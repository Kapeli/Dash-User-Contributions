# Transformers Docset

[Transformers](https://github.com/huggingface/transformers) by
[Hugging Face](https://huggingface.co) provides state-of-the-art architectures
for Natural Language Processing, Computer Vision, Audio, Video, and Multimodal
tasks — for both inference and training.

> **Note** I am not affiliated with the Hugging Face team. I created this Dash
> docset because I love the library and Dash.

## Author

**Venkat**
GitHub: [venkatasg](https://github.com/venkatasg)
Twitter: [@_venkatasg](https://twitter.com/_venkatasg)

---

## Building the Docset

The `generate_docset.py` script downloads the rendered documentation from
[huggingface.co/docs/transformers](https://huggingface.co/docs/transformers)
and packages it into a Dash-compatible `.docset` bundle.

### Prerequisites

Python 3.10+ and the following packages:

```bash
pip install requests beautifulsoup4 pyyaml lxml
```

### Usage

```bash
# Build the docset for the latest published version (fetched from PyPI)
python generate_docset.py

# Pin to a specific version
python generate_docset.py --version 4.47.0

# Write the output somewhere other than the script directory
python generate_docset.py --output-dir ~/Desktop

# Speed up downloads with more parallel workers (be polite — default is 8)
python generate_docset.py --workers 12

# Skip the .tgz archive step (faster for local testing)
python generate_docset.py --no-archive

# Skip bundling the HuggingFace compiled CSS
# (pages will load it from the CDN — requires internet access inside Dash)
python generate_docset.py --skip-hf-css
```

The script will create:

```
transformers.docset/         ← Dash docset bundle
transformers.tgz             ← Archive ready for submission
```

### What the script does

1. **Fetches navigation** — downloads `_toctree.yml` from the transformers
   GitHub repository to discover all ~629 documentation pages.
2. **Downloads pages** — fetches each rendered HTML page from
   `huggingface.co/docs/transformers/vX.Y.Z/en/<slug>` in parallel.
3. **Bundles HF CSS** — downloads the HuggingFace compiled Tailwind CSS once
   so the docset renders correctly without an internet connection.
4. **Injects `hidesidebar.css`** — hides the top navigation bar, left sidebar,
   and right table-of-contents sidebar so the Dash viewer shows only the
   documentation content.
5. **Adds Dash anchors** — inserts
   `<a name="//apple_ref/cpp/Class/…" class="dashAnchor">` before every API
   entry (classes, functions, methods) so they appear in Dash's search index.
6. **Builds the SQLite index** — creates `docSet.dsidx` with entries for
   classes, functions, methods, sections, and guide pages.
7. **Writes `Info.plist`** — sets the docset metadata including the fallback URL
   and keyword (`transformers`).
8. **Archives** — packages everything into `transformers.tgz`.

### Submitting a new version

After generating the docset, follow the standard
[Dash User Contributions](https://github.com/Kapeli/Dash-User-Contributions)
submission process:

1. Copy the `.tgz` to the appropriate `versions/X.Y.Z/` subdirectory.
2. Update `docset.json` with the new version number and add an entry to
   `specific_versions`.
3. Open a pull request.

---

## Visual notes

The HuggingFace docs site uses a SvelteKit frontend with Tailwind CSS. A few
layout quirks may be visible depending on Dash window width:

- A thin breadcrumb bar at the top of each page is intentionally kept — it
  shows the current page path and is useful for navigation context.
- If you resize the Dash window very narrow the content may wrap differently
  than on the website; this is expected Tailwind responsive behaviour.
