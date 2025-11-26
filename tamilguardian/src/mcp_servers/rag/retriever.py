import os
import asyncio
from typing import Dict, Any, List, Optional
import httpx
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class NebiusRAGRetriever:
    """RAG retriever using Nebius for embeddings and vector search"""
    
    def __init__(self):
        self.nebius_api_key = os.getenv("NEBIUS_API_KEY")
        self.nebius_base_url = "https://api.nebius.ai/v1"
        self.client = httpx.AsyncClient()
        
        # Local fallback embedder
        self.local_embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # FAISS index (in production, this would be persistent)
        self.index = None
        self.documents = []
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index with sample Tamil Nadu legal documents"""
        # Sample documents (in production, load from database)
        sample_docs = [
            {
                "doc_id": "tn_rent_control_act_2019",
                "title": "Tamil Nadu Rent Control Act 2019",
                "content": "The Tamil Nadu Rent Control Act, 2019 regulates rental agreements and tenant rights in Tamil Nadu. Section 4 provides for fair rent determination...",
                "jurisdiction": "tamil_nadu",
                "source_type": "statute"
            },
            {
                "doc_id": "tn_shops_establishments_act",
                "title": "Tamil Nadu Shops and Establishments Act",
                "content": "This Act regulates working conditions in shops and commercial establishments. Section 12 mandates maximum working hours...",
                "jurisdiction": "tamil_nadu",
                "source_type": "statute"
            },
            {
                "doc_id": "consumer_protection_act_2019",
                "title": "Consumer Protection Act 2019",
                "content": "The Consumer Protection Act, 2019 provides for consumer rights and remedies. Section 35 establishes consumer dispute redressal commissions...",
                "jurisdiction": "india",
                "source_type": "statute"
            }
        ]
        
        # Create embeddings
        embeddings = []
        for doc in sample_docs:
            embedding = self.local_embedder.encode(doc["content"])
            embeddings.append(embedding)
            self.documents.append(doc)
        
        # Initialize FAISS index
        if embeddings:
            embeddings_array = np.array(embeddings).astype('float32')
            self.index = faiss.IndexFlatIP(embeddings_array.shape[1])
            self.index.add(embeddings_array)
    
    async def health_check(self) -> Dict[str, str]:
        """Check retriever health"""
        try:
            if self.nebius_api_key:
                # Test Nebius connection
                response = await self.client.get(
                    f"{self.nebius_base_url}/health",
                    headers={"Authorization": f"Bearer {self.nebius_api_key}"}
                )
                if response.status_code == 200:
                    return {"status": "healthy", "backend": "nebius"}
            
            # Fallback to local
            return {"status": "healthy", "backend": "local"}
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        jurisdiction_boost: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        
        try:
            # Get query embedding
            if self.nebius_api_key:
                query_embedding = await self._get_nebius_embedding(query)
            else:
                query_embedding = self.local_embedder.encode(query)
            
            # Search FAISS index
            scores, indices = self.index.search(
                np.array([query_embedding]).astype('float32'),
                min(top_k, len(self.documents))
            )
            
            # Format results with jurisdiction boosting
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0:  # Valid index
                    doc = self.documents[idx].copy()
                    doc["score"] = float(score)
                    
                    # Apply jurisdiction boost
                    if jurisdiction_boost:
                        jurisdiction = doc.get("jurisdiction", "unknown")
                        boost = jurisdiction_boost.get(jurisdiction, 1.0)
                        doc["score"] *= boost
                    
                    results.append(doc)
            
            # Sort by boosted score
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def _get_nebius_embedding(self, text: str) -> np.ndarray:
        """Get embedding from Nebius API"""
        try:
            response = await self.client.post(
                f"{self.nebius_base_url}/embeddings",
                headers={"Authorization": f"Bearer {self.nebius_api_key}"},
                json={
                    "model": "text-embedding-ada-002",
                    "input": text
                }
            )
            response.raise_for_status()
            
            data = response.json()
            return np.array(data["data"][0]["embedding"])
            
        except Exception as e:
            logger.warning(f"Nebius embedding failed, using local: {e}")
            return self.local_embedder.encode(text)
    
    async def index_document(self, document: Dict[str, Any]) -> str:
        """Index a new document"""
        try:
            # Generate embedding
            content = document.get("content", "")
            if self.nebius_api_key:
                embedding = await self._get_nebius_embedding(content)
            else:
                embedding = self.local_embedder.encode(content)
            
            # Add to index
            self.index.add(np.array([embedding]).astype('float32'))
            self.documents.append(document)
            
            return document.get("doc_id", f"doc_{len(self.documents)}")
            
        except Exception as e:
            logger.error(f"Document indexing failed: {e}")
            raise