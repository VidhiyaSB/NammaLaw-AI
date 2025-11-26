from typing import Dict, Any, List
from ..base import BaseMCPServer
import PyPDF2
from docx import Document
import io
import re
import logging

logger = logging.getLogger(__name__)

class ParserMCPServer(BaseMCPServer):
    """MCP Server for document parsing operations"""
    
    def __init__(self):
        super().__init__("parser", "http://localhost:8004")
    
    async def health_check(self) -> Dict[str, str]:
        """Check parser server health"""
        return {"status": "healthy", "service": "parser"}
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parser tool calls"""
        
        if tool_name == "parse_documents":
            return await self._parse_documents(params)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _parse_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse uploaded documents and extract key information"""
        documents = params.get("documents", [])
        
        try:
            all_facts = []
            all_entities = []
            
            for doc_bytes in documents:
                # Determine document type and parse
                text = self._extract_text(doc_bytes)
                
                # Extract structured information
                facts = self._extract_facts(text)
                entities = self._extract_entities(text)
                
                all_facts.extend(facts)
                all_entities.extend(entities)
            
            return {
                "success": True,
                "facts": all_facts,
                "entities": all_entities,
                "summary": f"Parsed {len(documents)} documents, extracted {len(all_facts)} facts"
            }
            
        except Exception as e:
            logger.error(f"Document parsing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_text(self, doc_bytes: bytes) -> str:
        """Extract text from document bytes"""
        try:
            # Try PDF first
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(doc_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except:
            try:
                # Try DOCX
                doc = Document(io.BytesIO(doc_bytes))
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except:
                # Assume plain text
                return doc_bytes.decode('utf-8', errors='ignore')
    
    def _extract_facts(self, text: str) -> List[str]:
        """Extract key facts from document text"""
        facts = []
        
        # Date patterns
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        dates = re.findall(date_pattern, text)
        for date in dates:
            facts.append(f"Date mentioned: {date}")
        
        # Amount patterns
        amount_pattern = r'₹\s*[\d,]+(?:\.\d{2})?|Rs\.?\s*[\d,]+(?:\.\d{2})?'
        amounts = re.findall(amount_pattern, text)
        for amount in amounts:
            facts.append(f"Amount mentioned: {amount}")
        
        # Address patterns (basic)
        address_pattern = r'\b\d+[^,\n]*(?:street|road|avenue|nagar|colony)[^,\n]*\b'
        addresses = re.findall(address_pattern, text, re.IGNORECASE)
        for address in addresses:
            facts.append(f"Address mentioned: {address.strip()}")
        
        # Legal terms
        legal_terms = [
            'agreement', 'contract', 'lease', 'rent', 'deposit', 'notice',
            'eviction', 'termination', 'breach', 'violation', 'damages',
            'compensation', 'refund', 'penalty'
        ]
        
        for term in legal_terms:
            if term.lower() in text.lower():
                # Find context around the term
                pattern = rf'.{{0,50}}\b{re.escape(term)}\b.{{0,50}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:3]:  # Limit to 3 matches per term
                    facts.append(f"Legal context: {match.strip()}")
        
        return facts[:20]  # Limit to top 20 facts
    
    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text"""
        entities = []
        
        # Phone numbers
        phone_pattern = r'\b(?:\+91|0)?[6-9]\d{9}\b'
        phones = re.findall(phone_pattern, text)
        for phone in phones:
            entities.append({"type": "phone", "value": phone})
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for email in emails:
            entities.append({"type": "email", "value": email})
        
        # Names (basic pattern - capitalized words)
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
        names = re.findall(name_pattern, text)
        for name in names[:5]:  # Limit to 5 names
            entities.append({"type": "person", "value": name})
        
        return entities