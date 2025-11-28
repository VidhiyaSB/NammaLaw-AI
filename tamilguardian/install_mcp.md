# MCP Installation Guide

## Python MCP Packages
```bash
pip install -r requirements.txt
```

## Node.js MCP Packages
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

## Verify Installation
```bash
# Check Python MCP servers
python -m perplexity_mcp_server --help
python -m mcp_server_sqlite --help
python -m elevenlabs_mcp --help

# Check Node.js MCP server
npx @modelcontextprotocol/server-filesystem --help
```

## Test MCP Setup
```bash
python test_mcp.py
```

## Current Status
✅ RAG Server - Working (5 TN legal documents)
⏳ Official MCP Servers - Ready for installation on another device