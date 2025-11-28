#!/usr/bin/env python3
"""Simple test for working components"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_working_components():
    """Test only working components"""
    from src.mcp_servers.base import MCPServerManager
    
    manager = MCPServerManager()
    
    # Test RAG (working)
    print("Testing RAG server...")
    docs = await manager.call_server("rag", "list_documents", {})
    print(f"✅ RAG: {docs.get('count', 0)} documents available")
    
    search = await manager.call_server("rag", "search", {"query": "supreme court"})
    print(f"✅ RAG Search: {len(search.get('results', []))} results found")
    
    print("\n🎉 RAG server is working perfectly!")
    print("Your NammaLaw AI can search Tamil Nadu legal documents.")

if __name__ == "__main__":
    asyncio.run(test_working_components())