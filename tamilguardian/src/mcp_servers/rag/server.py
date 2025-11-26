from typing import Dict, Any, List
from ..base import BaseMCPServer
from .retriever import NebiusRAGRetriever
import logging

logger = logging.getLogger(__name__)

class RAGMCPServer(BaseMCPServer):
    """MCP Server for RAG operations using Nebius"""
    
    def __init__(self):
        super().__init__("rag", "http://localhost:8001")  # In production, this would be a separate service
        self.retriever = NebiusRAGRetriever()
    
    async def health_check(self) -> Dict[str, str]:
        """Check RAG server health"""
        try:
            # Test retriever connection
            await self.retriever.health_check()
            return {"status": "healthy", "service": "rag"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle RAG tool calls"""
        
        if tool_name == "search":
            return await self._search(params)
        elif tool_name == "index_document":
            return await self._index_document(params)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform RAG search with Tamil Nadu jurisdiction boosting"""
        query = params.get("query", "")
        top_k = params.get("top_k", 10)
        
        try:
            results = await self.retriever.search(
                query=query,
                top_k=top_k,
                jurisdiction_boost={"tamil_nadu": 1.5, "india": 1.2}
            )
            
            # Calculate confidence based on scores
            confidence = self._calculate_confidence(results)
            
            return {
                "success": True,
                "results": results,
                "confidence": confidence,
                "sources": [self._format_citation(r) for r in results]
            }
            
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "confidence": 0.0
            }
    
    async def _index_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Index a new document"""
        document = params.get("document", {})
        
        try:
            doc_id = await self.retriever.index_document(document)
            return {
                "success": True,
                "doc_id": doc_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_confidence(self, results: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not results:
            return 0.0
        
        # Weight by jurisdiction and score
        total_score = 0.0
        total_weight = 0.0
        
        for result in results:
            jurisdiction = result.get("jurisdiction", "unknown")
            score = result.get("score", 0.0)
            
            # Jurisdiction weights
            weight = 1.0
            if jurisdiction == "tamil_nadu":
                weight = 1.5
            elif jurisdiction == "india":
                weight = 1.2
            
            total_score += score * weight
            total_weight += weight
        
        return min(total_score / total_weight if total_weight > 0 else 0.0, 1.0)
    
    def _format_citation(self, result: Dict) -> Dict[str, str]:
        """Format search result as citation"""
        return {
            "doc_id": result.get("doc_id", ""),
            "title": result.get("title", ""),
            "source_type": result.get("source_type", "statute"),
            "jurisdiction": result.get("jurisdiction", "unknown"),
            "confidence": result.get("score", 0.0),
            "excerpt": result.get("content", "")[:200] + "..."
        }