#!/usr/bin/env npx tsx
/**
 * HOL Docset Generator for Dash/Zeal
 * Scrapes hol.org documentation and creates a Dash-compatible docset
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

const DOCSET_NAME = 'Hashgraph_Online';
const BASE_URL = 'https://hol.org';

/** Simple SQLite wrapper using native sqlite3 command */
class SQLiteDB {
  constructor(private dbPath: string) {
    // Create the database and table
    this.exec('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);');
    this.exec('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);');
  }
  
  exec(sql: string): void {
    execSync(`sqlite3 "${this.dbPath}" "${sql.replace(/"/g, '\\"')}"`, { encoding: 'utf-8' });
  }
  
  insert(name: string, type: string, docPath: string): void {
    const escapedName = name.replace(/'/g, "''");
    const escapedPath = docPath.replace(/'/g, "''");
    this.exec(`INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('${escapedName}', '${type}', '${escapedPath}');`);
  }
}

interface DocEntry {
  name: string;
  type: string;
  path: string;
}

/** Documentation structure to scrape */
const DOC_STRUCTURE: Array<{ url: string; name: string; type: string }> = [
  // Registry Broker
  { url: '/docs/registry-broker/', name: 'Registry Broker Overview', type: 'Guide' },
  { url: '/docs/registry-broker/getting-started/quick-start', name: 'Quick Start Guide', type: 'Guide' },
  { url: '/docs/registry-broker/getting-started/installation', name: 'Installation & Setup', type: 'Guide' },
  { url: '/docs/registry-broker/getting-started/first-registration', name: 'First Agent Registration', type: 'Guide' },
  { url: '/docs/registry-broker/getting-started/faq', name: 'FAQ', type: 'Guide' },
  { url: '/docs/registry-broker/search', name: 'Search & Discovery', type: 'Guide' },
  { url: '/docs/registry-broker/erc-8004-solana', name: 'ERC-8004 on Solana', type: 'Guide' },
  { url: '/docs/registry-broker/chat', name: 'Chat Guide', type: 'Guide' },
  { url: '/docs/registry-broker/feedback', name: 'Agent Feedback', type: 'Guide' },
  { url: '/docs/registry-broker/xmtp', name: 'XMTP Integration', type: 'Guide' },
  { url: '/docs/registry-broker/mcp-server', name: 'Hashnet MCP Server', type: 'Guide' },
  { url: '/docs/registry-broker/encrypted-chat', name: 'Encrypted Chat', type: 'Guide' },
  { url: '/docs/registry-broker/ledger-auth-credits', name: 'Ledger Auth & Credits', type: 'Guide' },
  { url: '/docs/registry-broker/api/client', name: 'API Client Reference', type: 'Class' },
  { url: '/docs/registry-broker/multi-protocol-chat', name: 'Multi-Protocol Chat', type: 'Guide' },
  
  // Standards SDK
  { url: '/docs/libraries/standards-sdk/', name: 'Standards SDK', type: 'Library' },
  { url: '/docs/libraries/standards-sdk/overview', name: 'SDK Overview', type: 'Guide' },
  { url: '/docs/libraries/standards-sdk/cli', name: 'Standards SDK CLI', type: 'Command' },
  { url: '/docs/libraries/standards-sdk/hcs-2/', name: 'HCS-2: Topic Registries', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-3/', name: 'HCS-3: Resource Recursion', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-5/', name: 'HCS-5: Hashinals', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-6/', name: 'HCS-6: Dynamic Hashinals', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-7/', name: 'HCS-7: Smart Hashinals', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-10/', name: 'HCS-10: OpenConvAI', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-11/', name: 'HCS-11: Profile Metadata', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-12/', name: 'HCS-12: HashLinks', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-14/', name: 'HCS-14: Universal Agent ID', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-15/', name: 'HCS-15: Petal Accounts', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-16/', name: 'HCS-16: Flora Coordination', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-17/', name: 'HCS-17: State Hash Calculation', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-18/', name: 'HCS-18: Flora Discovery', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-20/', name: 'HCS-20: Auditable Points', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/hcs-21/', name: 'HCS-21: Adapter Registry', type: 'Protocol' },
  { url: '/docs/libraries/standards-sdk/inscribe', name: 'Inscribe: File Utilities', type: 'Function' },
  { url: '/docs/libraries/standards-sdk/utils-services', name: 'Utilities and Services', type: 'Module' },
  { url: '/docs/libraries/standards-sdk/registry-broker-client', name: 'Registry Broker Client', type: 'Class' },
  { url: '/docs/libraries/standards-sdk/configuration', name: 'Configuration', type: 'Guide' },
  
  // Standards Specifications
  { url: '/docs/standards/hcs-1', name: 'HCS-1: File Storage', type: 'Protocol' },
  { url: '/docs/standards/hcs-2', name: 'HCS-2: Discovery Registries', type: 'Protocol' },
  { url: '/docs/standards/hcs-3', name: 'HCS-3: Resource Linking', type: 'Protocol' },
  { url: '/docs/standards/hcs-4', name: 'HCS-4: Standardization Process', type: 'Protocol' },
  { url: '/docs/standards/hcs-5', name: 'HCS-5: Dynamic NFTs', type: 'Protocol' },
  { url: '/docs/standards/hcs-10', name: 'HCS-10: AI Agent Communication', type: 'Protocol' },
  { url: '/docs/standards/hcs-11', name: 'HCS-11: Identity Profiles', type: 'Protocol' },
  { url: '/docs/standards/hcs-14', name: 'HCS-14: Universal Agent ID', type: 'Protocol' },
  
  // Other Libraries
  { url: '/docs/libraries/conversational-agent/', name: 'Conversational Agent', type: 'Library' },
  { url: '/docs/libraries/conversational-agent/overview', name: 'Conversational Agent Overview', type: 'Guide' },
  { url: '/docs/libraries/standards-agent-kit/', name: 'Standards Agent Kit', type: 'Library' },
  { url: '/docs/libraries/hashinal-wc/', name: 'Hashinal Wallet Connect', type: 'Library' },
  { url: '/docs/libraries/recursion-sdk/', name: 'Recursion SDK', type: 'Library' },
];

async function fetchPage(url: string): Promise<string> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}: ${response.status}`);
  }
  return response.text();
}

function extractMainContent(html: string, pageUrl: string): string {
  // Extract the main article content from Docusaurus pages
  const articleMatch = html.match(/<article[^>]*>([\s\S]*?)<\/article>/i);
  const mainMatch = html.match(/<main[^>]*>([\s\S]*?)<\/main>/i);
  
  let content = articleMatch?.[0] || mainMatch?.[0] || html;
  
  // Clean up the HTML
  // Remove scripts
  content = content.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
  // Remove navigation elements
  content = content.replace(/<nav[^>]*>[\s\S]*?<\/nav>/gi, '');
  // Remove footer
  content = content.replace(/<footer[^>]*>[\s\S]*?<\/footer>/gi, '');
  
  // Rewrite relative URLs to absolute
  content = content.replace(/href="\//g, `href="${BASE_URL}/`);
  content = content.replace(/src="\//g, `src="${BASE_URL}/`);
  
  // Create a complete HTML document
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HOL Documentation</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; }
    pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
    code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; }
    pre code { background: none; padding: 0; }
    h1, h2, h3 { color: #333; }
    a { color: #0066cc; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background: #f5f5f5; }
  </style>
</head>
<body>
<!-- Online page at ${BASE_URL}${pageUrl} -->
${content}
</body>
</html>`;
}

async function main() {
  const docsetPath = path.join(process.cwd(), `${DOCSET_NAME}.docset`);
  const contentsPath = path.join(docsetPath, 'Contents');
  const resourcesPath = path.join(contentsPath, 'Resources');
  const documentsPath = path.join(resourcesPath, 'Documents');
  
  // Create directory structure
  console.log('Creating docset structure...');
  fs.mkdirSync(documentsPath, { recursive: true });
  
  // Create Info.plist
  const infoPlist = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleIdentifier</key>
  <string>hashgraph-online</string>
  <key>CFBundleName</key>
  <string>Hashgraph Online</string>
  <key>DocSetPlatformFamily</key>
  <string>hol</string>
  <key>isDashDocset</key>
  <true/>
  <key>dashIndexFilePath</key>
  <string>docs/registry-broker/index.html</string>
  <key>DashDocSetFamily</key>
  <string>dashtoc</string>
  <key>DashDocSetFallbackURL</key>
  <string>https://hol.org</string>
  <key>isJavaScriptEnabled</key>
  <false/>
</dict>
</plist>`;
  
  fs.writeFileSync(path.join(contentsPath, 'Info.plist'), infoPlist);
  console.log('Created Info.plist');
  
  // Create SQLite database
  const dbPath = path.join(resourcesPath, 'docSet.dsidx');
  if (fs.existsSync(dbPath)) {
    fs.unlinkSync(dbPath);
  }
  
  const db = new SQLiteDB(dbPath);
  
  console.log('Fetching documentation pages...');
  
  for (const doc of DOC_STRUCTURE) {
    const fullUrl = `${BASE_URL}${doc.url}`;
    console.log(`  Fetching: ${doc.name}`);
    
    try {
      const html = await fetchPage(fullUrl);
      const cleanHtml = extractMainContent(html, doc.url);
      
      // Create file path
      const relativePath = doc.url.replace(/^\//, '').replace(/\/$/, '/index') + '.html';
      const filePath = path.join(documentsPath, relativePath);
      
      // Ensure directory exists
      fs.mkdirSync(path.dirname(filePath), { recursive: true });
      
      // Write HTML file
      fs.writeFileSync(filePath, cleanHtml);
      
      // Add to index
      db.insert(doc.name, doc.type, relativePath);
      
      // Small delay to be nice to the server
      await new Promise(resolve => setTimeout(resolve, 100));
    } catch (error) {
      console.error(`  Error fetching ${doc.name}: ${error}`);
    }
  }
  
  console.log('Created SQLite index');
  
  // Create index page
  const indexHtml = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Hashgraph Online Documentation</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
    h1 { color: #333; }
    a { color: #0066cc; text-decoration: none; }
    a:hover { text-decoration: underline; }
    ul { list-style: none; padding: 0; }
    li { padding: 8px 0; border-bottom: 1px solid #eee; }
    .category { font-weight: bold; margin-top: 20px; color: #666; }
  </style>
</head>
<body>
  <h1>Hashgraph Online (HOL) Documentation</h1>
  <p>Universal Agentic Registry - AI Agent Discovery, Communication, and Identity</p>
  
  <h2>Registry Broker</h2>
  <ul>
    <li><a href="docs/registry-broker/index.html">Overview</a></li>
    <li><a href="docs/registry-broker/getting-started/quick-start.html">Quick Start</a></li>
    <li><a href="docs/registry-broker/api/client.html">API Reference</a></li>
    <li><a href="docs/registry-broker/mcp-server.html">MCP Server</a></li>
  </ul>
  
  <h2>Standards SDK</h2>
  <ul>
    <li><a href="docs/libraries/standards-sdk/index.html">SDK Overview</a></li>
    <li><a href="docs/libraries/standards-sdk/cli.html">CLI Reference</a></li>
  </ul>
  
  <h2>HCS Standards</h2>
  <ul>
    <li><a href="docs/standards/hcs-1.html">HCS-1: File Storage</a></li>
    <li><a href="docs/standards/hcs-10.html">HCS-10: AI Agent Communication</a></li>
    <li><a href="docs/standards/hcs-14.html">HCS-14: Universal Agent ID</a></li>
  </ul>
  
  <p style="margin-top: 40px; color: #666;">
    <a href="https://hol.org">hol.org</a> | 
    <a href="https://hol.org/registry">Universal Registry</a> | 
    <a href="https://github.com/hashgraph-online/standards-sdk">GitHub</a>
  </p>
</body>
</html>`;
  
  fs.writeFileSync(path.join(documentsPath, 'index.html'), indexHtml);
  console.log('Created index page');
  
  console.log(`\nDocset created at: ${docsetPath}`);
  console.log('\nNext steps:');
  console.log('1. Add icon.png (16x16) and icon@2x.png (32x32) to the docset root');
  console.log(`2. Archive: tar --exclude='.DS_Store' -cvzf ${DOCSET_NAME}.tgz ${DOCSET_NAME}.docset`);
}

main().catch(console.error);
