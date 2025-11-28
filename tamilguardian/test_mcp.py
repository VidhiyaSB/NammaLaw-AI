#!/usr/bin/env python3
"""Test MCP integration"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_mcp():
    """Test MCP servers"""
    from src.mcp_servers.base import MCPServerManager
    
    manager = MCPServerManager()
    
    # Test primary RAG server
    print("Testing RAG server (primary)...")
    
    # List available documents
    docs = await manager.call_server("rag", "list_documents", {})
    print(f"Available docs: {docs.get('count', 0)}")
    
    # Search documents
    rag_result = await manager.call_server("rag", "search", {
        "query": "supreme court judgments"
    })
    print(f"RAG search: {rag_result.get('success', False)}")
    if rag_result.get('success'):
        print(f"Found {len(rag_result.get('results', []))} results")
    
    # Test fallback Perplexity MCP server
    print("\nTesting Perplexity MCP (fallback)...")
    try:
        result = await manager.call_mcp_tool("perplexity_official", "search", {
            "query": "legal aid in Tamil Nadu"
        })
        print(f"Perplexity Official: {result.get('success', False)}")
    except Exception as e:
        print(f"Perplexity: Error - {e}")
    
    # Test filesystem MCP server
    print("\nTesting filesystem MCP server...")
    try:
        fs_result = await manager.call_mcp_tool("filesystem", "list_directory", {
            "path": "."
        })
        print(f"Filesystem: {fs_result.get('success', False)}")
    except Exception as e:
        print(f"Filesystem: Error - {e}")
    
    # Test SQLite MCP server
    print("\nTesting SQLite MCP server...")
    try:
        sqlite_result = await manager.call_mcp_tool("sqlite", "list_tables", {})
        print(f"SQLite: {sqlite_result.get('success', False)}")
    except Exception as e:
        print(f"SQLite: Error - {e}")
    
    # Test ElevenLabs MCP server
    print("\nTesting ElevenLabs MCP server...")
    try:
        elevenlabs_result = await manager.call_mcp_tool("elevenlabs", "text_to_speech", {
            "text": "Hello from NammaLaw AI"
        })
        print(f"ElevenLabs: {elevenlabs_result.get('success', False)}")
    except Exception as e:
        print(f"ElevenLabs: Error - {e}")
    
    # List available tools
    tools = await manager.list_mcp_tools("elevenlabs")
    print(f"ElevenLabs tools: {tools.get('tools', [])}")

if __name__ == "__main__":
    asyncio.run(test_mcp())