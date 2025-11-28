"""Official MCP servers integration for NammaLaw AI"""

from .base import MCPServerManager
from .official_mcp import mcp_client, setup_official_servers

__all__ = ["MCPServerManager", "mcp_client", "setup_official_servers"]