from typing import Dict, Any
from ..base import BaseMCPServer
import openai
import os
import json
import logging

logger = logging.getLogger(__name__)

class LLMMCPServer(BaseMCPServer):
    """MCP Server for LLM operations"""
    
    def __init__(self):
        super().__init__("llm", "http://localhost:8002")
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def health_check(self) -> Dict[str, str]:
        """Check LLM server health"""
        try:
            # Test API connection
            await self.client.models.list()
            return {"status": "healthy", "service": "llm"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LLM tool calls"""
        
        if tool_name == "reason":
            return await self._reason(params)
        elif tool_name == "generate":
            return await self._generate(params)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _reason(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform legal reasoning on the query and context"""
        query = params.get("query", "")
        context = params.get("context", {})
        
        # Extract relevant context
        rag_results = context.get("rag_retrieval", {}).get("results", [])
        web_results = context.get("web_search", {}).get("results", [])
        parsed_docs = context.get("parse_documents", {}).get("facts", [])
        
        # Build context string
        context_str = self._build_context_string(rag_results, web_results, parsed_docs)
        
        system_prompt = """You are TamilGuardian, an AI legal assistant for Tamil Nadu residents. 
        Analyze the legal query using the provided context and generate a clear, factual summary.
        
        CRITICAL REQUIREMENTS:
        1. Every factual claim MUST include a citation [doc_id]
        2. Prioritize Tamil Nadu laws over India-level laws
        3. Be clear about limitations and when to consult a lawyer
        4. Use simple, accessible language
        5. Include relevant legal sections and provisions
        
        Respond in JSON format with: summary, key_points, legal_basis, confidence_level"""
        
        user_prompt = f"""
        Legal Query: {query}
        
        Available Context:
        {context_str}
        
        Provide a comprehensive legal analysis with proper citations."""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text
            try:
                result = json.loads(content)
            except:
                result = {"summary": content}
            
            return {
                "success": True,
                **result
            }
            
        except Exception as e:
            logger.error(f"LLM reasoning failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate legal documents or options"""
        generation_type = params.get("type", "options")
        context = params.get("context", {})
        
        if generation_type == "options":
            return await self._generate_options(context)
        elif generation_type == "draft":
            return await self._generate_draft(context)
        else:
            raise ValueError(f"Unknown generation type: {generation_type}")
    
    async def _generate_options(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate legal options and next steps"""
        reasoning = context.get("llm_reasoning", {})
        
        system_prompt = """Generate 3-5 practical legal options for the user's situation.
        Each option should include: title, description, steps, estimated_cost, timeline, success_probability.
        
        Respond in JSON format with an 'options' array."""
        
        user_prompt = f"""
        Based on this legal analysis:
        {reasoning.get('summary', '')}
        
        Key Points: {reasoning.get('key_points', [])}
        Legal Basis: {reasoning.get('legal_basis', '')}
        
        Generate practical options for the user."""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return {
                "success": True,
                **result
            }
            
        except Exception as e:
            logger.error(f"Options generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_draft(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate legal document draft"""
        reasoning = context.get("llm_reasoning", {})
        options = context.get("generate_options", {}).get("options", [])
        
        # Use the first option as basis for draft
        selected_option = options[0] if options else {}
        
        system_prompt = """Draft a formal legal notice or complaint based on the analysis.
        Use proper legal formatting, include all necessary sections, and maintain professional tone.
        Include placeholders for user-specific information like [YOUR_NAME], [DATE], etc."""
        
        user_prompt = f"""
        Legal Analysis: {reasoning.get('summary', '')}
        Selected Option: {selected_option.get('title', '')} - {selected_option.get('description', '')}
        
        Draft a formal legal document."""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            return {
                "success": True,
                "content": content,
                "document_type": "legal_notice"
            }
            
        except Exception as e:
            logger.error(f"Draft generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_context_string(self, rag_results, web_results, parsed_docs) -> str:
        """Build context string from various sources"""
        context_parts = []
        
        # RAG results
        if rag_results:
            context_parts.append("=== LEGAL DOCUMENTS ===")
            for result in rag_results[:5]:  # Top 5 results
                context_parts.append(f"[{result.get('doc_id', 'unknown')}] {result.get('title', '')}")
                context_parts.append(f"Jurisdiction: {result.get('jurisdiction', 'unknown')}")
                context_parts.append(f"Content: {result.get('content', '')[:500]}...")
                context_parts.append("")
        
        # Web results
        if web_results:
            context_parts.append("=== WEB SOURCES ===")
            for result in web_results[:3]:  # Top 3 web results
                context_parts.append(f"[web_{result.get('url', 'unknown')}] {result.get('title', '')}")
                context_parts.append(f"Content: {result.get('content', '')[:300]}...")
                context_parts.append("")
        
        # Parsed documents
        if parsed_docs:
            context_parts.append("=== USER DOCUMENTS ===")
            for fact in parsed_docs[:10]:  # Top 10 facts
                context_parts.append(f"- {fact}")
            context_parts.append("")
        
        return "\n".join(context_parts)