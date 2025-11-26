from typing import Dict, Any, List
from ..base import BaseMCPServer
import httpx
import os
import logging

logger = logging.getLogger(__name__)

class WebSearchMCPServer(BaseMCPServer):
    """MCP Server for web search operations"""
    
    def __init__(self):
        super().__init__("websearch", "http://localhost:8003")
        self.search_api_key = os.getenv("SEARCH_API_KEY")  # Google Custom Search or similar
    
    async def health_check(self) -> Dict[str, str]:
        """Check web search server health"""
        return {"status": "healthy", "service": "websearch"}
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web search tool calls"""
        
        if tool_name == "search":
            return await self._search(params)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform web search for legal information"""
        query = params.get("query", "")
        
        # Enhance query with Tamil Nadu context
        enhanced_query = f"{query} Tamil Nadu law legal rights"
        
        try:
            # Mock search results (in production, use actual search API)
            results = [
                {
                    "title": "Tamil Nadu Legal Services Authority",
                    "url": "https://tnlsa.tn.gov.in",
                    "content": "The Tamil Nadu Legal Services Authority provides free legal aid and services to eligible persons...",
                    "source_type": "web",
                    "jurisdiction": "tamil_nadu"
                },
                {
                    "title": "Consumer Rights in Tamil Nadu",
                    "url": "https://example.com/consumer-rights-tn",
                    "content": "Consumer protection laws in Tamil Nadu provide various remedies for defective products and services...",
                    "source_type": "web",
                    "jurisdiction": "tamil_nadu"
                }
            ]
            
            return {
                "success": True,
                "results": results,
                "sources": [self._format_web_citation(r) for r in results]
            }
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_web_citation(self, result: Dict) -> Dict[str, str]:
        """Format web search result as citation"""
        return {
            "doc_id": f"web_{result.get('url', '').replace('https://', '').replace('/', '_')}",
            "title": result.get("title", ""),
            "source_type": "web",
            "jurisdiction": result.get("jurisdiction", "web"),
            "confidence": 0.6,  # Lower confidence for web sources
            "excerpt": result.get("content", "")[:200] + "..."
        }