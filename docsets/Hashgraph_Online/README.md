# Hashgraph Online (HOL) Docset

## Author
- **GitHub**: [hashgraph-online](https://github.com/hashgraph-online)
- **Twitter/X**: [@HashgraphOnline](https://x.com/HashgraphOnline)

## What is Hashgraph Online?

Hashgraph Online (HOL) is the **Universal Agentic Registry** - a decentralized directory for AI Agents and MCP Servers. It provides blockchain-based identity, discovery, and encrypted communication for autonomous AI agents across Web2 and Web3.

**Key Features:**
- Agent discovery across 46,000+ indexed agents
- Multi-protocol support (A2A, MCP, XMTP, ERC-8004)
- Blockchain-based identity (HCS-14 Universal Agent ID)
- Encrypted agent-to-agent communication
- MCP server integration for Claude Desktop, Cursor IDE

## Documentation Source

- **Main Docs**: https://hol.org/docs/registry-broker/
- **SDK Docs**: https://hol.org/docs/libraries/standards-sdk/
- **Standards**: https://hol.org/docs/standards/hcs-1
- **Live Registry**: https://hol.org/registry

## How to Generate the Docset

### Prerequisites

- Node.js 20+
- pnpm (or npm)
- sqlite3 (usually pre-installed on macOS/Linux)
- ImageMagick (for icon generation)

### Generation Steps

The generation script (`generate-docset.ts`) is included in this folder.

```bash
# Create a working directory and copy the script
mkdir hol-docset && cd hol-docset
cp /path/to/generate-docset.ts .

# Create package.json
cat > package.json << 'EOF'
{
  "name": "hol-docset-generator",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "generate": "pnpm exec tsx generate-docset.ts"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "tsx": "^4.0.0",
    "typescript": "^5.0.0"
  }
}
EOF

# Install dependencies
pnpm install

# Generate docset
pnpm run generate

# Create icons (requires ImageMagick)
# Download icon from https://hol.org or use the one from hcs-improvement-proposals repo
magick /path/to/Logo_Icon.png -resize 16x16 Hashgraph_Online.docset/icon.png
magick /path/to/Logo_Icon.png -resize 32x32 Hashgraph_Online.docset/icon@2x.png

# Create archive
tar --exclude='.DS_Store' -cvzf Hashgraph_Online.tgz Hashgraph_Online.docset
```

### What the Script Does

1. Fetches documentation pages from hol.org (Docusaurus-based)
2. Extracts main content and creates clean, readable HTML
3. Creates a SQLite index (`docSet.dsidx`) for Dash search
4. Generates an `Info.plist` with proper docset metadata

## Indexed Content

The docset includes:
- **Registry Broker Documentation** - Agent discovery, chat, registration
- **Standards SDK** - Core SDK for HCS standards
- **HCS Standards** - 21+ protocol specifications (HCS-1 through HCS-21)
- **API Reference** - Complete API client documentation
- **Tutorials & Guides** - Getting started, MCP server setup, encrypted chat

## Known Issues

None currently. Please report issues at https://github.com/hashgraph-online/standards-sdk/issues

## Links

- **Website**: https://hol.org
- **GitHub**: https://github.com/hashgraph-online
- **npm**: `@hashgraphonline/standards-sdk`
- **Telegram**: https://t.me/hashinals
