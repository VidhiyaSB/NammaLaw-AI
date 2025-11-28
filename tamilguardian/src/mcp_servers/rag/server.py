from typing import Dict, Any, List
from ..base import BaseMCPServer
import os
import logging
import glob
from pathlib import Path

logger = logging.getLogger(__name__)

class RAGMCPServer(BaseMCPServer):
    """MCP Server for Tamil Nadu legal document retrieval"""
    
    def __init__(self):
        super().__init__("rag", "http://localhost:8001")
        self.legal_docs_path = os.path.join(os.path.dirname(__file__), "../../..", "data", "legal_docs")
        self.embeddings_path = os.path.join(os.path.dirname(__file__), "../../..", "data", "embeddings")
        self._load_documents()
        
    async def health_check(self) -> Dict[str, str]:
        """Check RAG server health"""
        return {"status": "healthy", "service": "rag"}
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle RAG tool calls"""
        
        if tool_name == "search":
            return await self._search(params)
        elif tool_name == "retrieve":
            return await self._retrieve(params)
        elif tool_name == "list_documents":
            return await self.list_documents()
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _load_documents(self):
        """Load available legal documents"""
        self.documents = []
        if os.path.exists(self.legal_docs_path):
            for file_path in glob.glob(os.path.join(self.legal_docs_path, "*.pdf")):
                doc_name = Path(file_path).stem
                self.documents.append({
                    "id": doc_name,
                    "title": doc_name.replace("_", " ").title(),
                    "path": file_path,
                    "type": "pdf"
                })
    
    async def _search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search Tamil Nadu legal documents"""
        query = params.get("query", "").lower()
        
        if not query:
            return {"success": False, "error": "No query provided"}
        
        try:
            # Simple keyword matching in document titles
            results = []
            for doc in self.documents:
                title_lower = doc["title"].lower()
                if any(keyword in title_lower for keyword in query.split()):
                    results.append({
                        "title": doc["title"],
                        "content": f"Document: {doc['title']}",
                        "source": doc["id"],
                        "path": doc["path"],
                        "relevance": 0.8
                    })
            
            # If no matches, return all documents
            if not results:
                results = [{
                    "title": doc["title"],
                    "content": f"Available document: {doc['title']}",
                    "source": doc["id"],
                    "path": doc["path"],
                    "relevance": 0.5
                } for doc in self.documents[:3]]  # Limit to 3
            
            return {
                "success": True,
                "results": results,
                "query": query,
                "source": "TN Legal Documents",
                "total_docs": len(self.documents)
            }
            
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _retrieve(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve specific legal document"""
        doc_id = params.get("doc_id", "")
        
        if not doc_id:
            return {"success": False, "error": "No document ID provided"}
        
        try:
            # Find document by ID
            doc = next((d for d in self.documents if d["id"] == doc_id), None)
            
            if not doc:
                return {"success": False, "error": f"Document {doc_id} not found"}
            
            document = {
                "id": doc["id"],
                "title": doc["title"],
                "path": doc["path"],
                "type": doc["type"],
                "metadata": {
                    "filename": os.path.basename(doc["path"]),
                    "size": os.path.getsize(doc["path"]) if os.path.exists(doc["path"]) else 0
                }
            }
            
            return {
                "success": True,
                "document": document,
                "source": "TN Legal Documents"
            }
            
        except Exception as e:
            logger.error(f"RAG retrieve failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_documents(self) -> Dict[str, Any]:
        """List all available legal documents"""
        return {
            "success": True,
            "documents": self.documents,
            "count": len(self.documents)
        }