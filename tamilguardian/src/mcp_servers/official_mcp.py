"""Official MCP server integration using subprocess"""

import asyncio
import subprocess
import json
import os
import logging

logger = logging.getLogger(__name__)

class OfficialMCPClient:
    """Simple client for official MCP servers using subprocess"""
    
    def __init__(self):
        self.servers = {}
    
    async def connect_server(self, name: str, command: list, env: dict = None):
        """Register server command"""
        self.servers[name] = {
            "command": command,
            "env": {**os.environ, **(env or {})}
        }
        logger.info(f"Registered {name} MCP server")
        return True
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        """Call tool via subprocess"""
        if server_name not in self.servers:
            return {"error": f"Server {server_name} not registered"}
        
        server = self.servers[server_name]
        
        try:
            # Create MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Run server process
            process = await asyncio.create_subprocess_exec(
                *server["command"],
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=server["env"]
            )
            
            # Send request
            request_json = json.dumps(request) + "\n"
            stdout, stderr = await asyncio.wait_for(
                process.communicate(request_json.encode()),
                timeout=30.0
            )
            
            if process.returncode != 0:
                return {"error": f"Process failed: {stderr.decode()}", "success": False}
            
            # Parse response
            if stdout:
                response = json.loads(stdout.decode().strip())
                if "error" in response:
                    return {"error": response["error"], "success": False}
                return {"result": response.get("result"), "success": True}
            
            return {"error": "No response", "success": False}
            
        except asyncio.TimeoutError:
            return {"error": "Request timeout", "success": False}
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {"error": str(e), "success": False}
    
    async def list_tools(self, server_name: str):
        """List available tools"""
        if server_name not in self.servers:
            return {"error": f"Server {server_name} not registered"}
        
        try:
            # Try to get tools list
            result = await self.call_tool(server_name, "list_tools", {})
            if result.get("success"):
                return {"success": True, "tools": result.get("result", [])}
            else:
                # Return common tools for known servers
                common_tools = {
                    "perplexity_official": ["search", "research"],
                    "filesystem": ["read_file", "write_file", "list_directory"],
                    "sqlite": ["read_query", "write_query", "list_tables"],
                    "elevenlabs": ["text_to_speech", "voice_clone"]
                }
                return {"success": True, "tools": common_tools.get(server_name, [])}
        except Exception as e:
            return {"error": str(e)}

# Global MCP client instance
mcp_client = OfficialMCPClient()

async def setup_official_servers():
    """Setup official MCP servers"""
    
    # Official Perplexity MCP server
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    if perplexity_key:
        await mcp_client.connect_server(
            "perplexity_official",
            ["python", "-m", "perplexity_mcp_server"],
            {
                "PERPLEXITY_API_KEY": perplexity_key,
                "PERPLEXITY_MODEL": "sonar-reasoning"
            }
        )
    
    # Official Filesystem MCP server
    await mcp_client.connect_server(
        "filesystem",
        ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."],
        {}
    )
    
    # Official SQLite MCP server
    await mcp_client.connect_server(
        "sqlite",
        ["python", "-m", "mcp_server_sqlite", "--db-path", "legal.db"],
        {}
    )
    
    # Official ElevenLabs MCP server
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    if elevenlabs_key:
        await mcp_client.connect_server(
            "elevenlabs",
            ["python", "-m", "elevenlabs_mcp"],
            {
                "ELEVENLABS_API_KEY": elevenlabs_key,
                "ELEVENLABS_MCP_OUTPUT_MODE": "files"
            }
        )