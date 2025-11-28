import asyncio
import httpx
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseMCPServer(ABC):
    """Base class for all MCP servers"""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @abstractmethod
    async def health_check(self) -> Dict[str, str]:
        """Check if server is healthy"""
        pass
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on this MCP server"""
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/{tool_name}",
                json=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error calling {self.name}.{tool_name}: {e}")
            raise

class MCPServerManager:
    """Manages connections to official MCP servers"""
    
    def __init__(self):
        self.servers: Dict[str, BaseMCPServer] = {}
        self._initialize_servers()
    
    def _initialize_servers(self):
        """Initialize MCP server connections"""
        from .official_mcp import mcp_client, setup_official_servers
        from .rag.server import RAGMCPServer
        
        # Primary: Custom RAG for TN legal data
        self.servers = {
            "rag": RAGMCPServer(),
        }
        
        # Official MCP client (fallback)
        self.mcp_client = mcp_client
        
        # Setup official servers
        asyncio.create_task(setup_official_servers())
    
    async def call_server(self, server_name: str, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on a specific server"""
        if server_name not in self.servers:
            raise ValueError(f"Unknown server: {server_name}")
        
        server = self.servers[server_name]
        return await server.call_tool(tool_name, params)
    
    async def health_check_all(self) -> Dict[str, str]:
        """Check health of all servers"""
        results = {}
        for name, server in self.servers.items():
            try:
                health = await server.health_check()
                results[name] = health.get("status", "unknown")
            except Exception as e:
                results[name] = f"error: {str(e)}"
        
        return results
    
    async def call_mcp_tool(self, server: str, tool: str, params: dict) -> dict:
        """Call official MCP tool"""
        return await self.mcp_client.call_tool(server, tool, params)
    
    async def list_mcp_tools(self, server: str) -> dict:
        """List tools for MCP server"""
        return await self.mcp_client.list_tools(server)