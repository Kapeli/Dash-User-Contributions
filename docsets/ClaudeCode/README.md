# Claude Code Docset

Maintained by [Clay Loveless](https://github.com/claylo).

## Generation

The docset is generated from the official [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code) using a custom pipeline in the [navel](https://github.com/claylo/navel) toolkit.

### Prerequisites

- Node.js 18+
- SQLite3

### Steps

1. Clone the navel repo and install dependencies:
   ```bash
   git clone https://github.com/claylo/navel.git
   cd navel
   npm install --prefix dash
   ```

2. Sync docs and build:
   ```bash
   bin/navel docs sync
   bin/navel dash
   ```

3. The docset is written to `build/ClaudeCode.docset`.

### What's included

- All pages from [code.claude.com](https://code.claude.com)
- Full-text search index
- Localized images for offline use
- Light and dark mode support

## Bug Reports

Open an issue at: https://github.com/claylo/navel/issues
