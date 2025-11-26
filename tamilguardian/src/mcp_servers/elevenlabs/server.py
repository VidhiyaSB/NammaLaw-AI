from typing import Dict, Any
from ..base import BaseMCPServer
import os
import httpx
import logging

logger = logging.getLogger(__name__)

class ElevenLabsMCPServer(BaseMCPServer):
    """MCP Server for ElevenLabs TTS operations"""
    
    def __init__(self):
        super().__init__("elevenlabs", "http://localhost:8005")
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
    
    async def health_check(self) -> Dict[str, str]:
        """Check ElevenLabs server health"""
        if not self.api_key:
            return {"status": "unhealthy", "error": "API key not configured"}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/voices",
                headers={"xi-api-key": self.api_key}
            )
            if response.status_code == 200:
                return {"status": "healthy", "service": "elevenlabs"}
            else:
                return {"status": "unhealthy", "error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ElevenLabs tool calls"""
        
        if tool_name == "synthesize":
            return await self._synthesize(params)
        elif tool_name == "list_voices":
            return await self._list_voices(params)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _synthesize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize text to speech"""
        text = params.get("text", "")
        voice_id = params.get("voice_id", "21m00Tcm4TlvDq8ikWAM")  # Default voice
        
        if not self.api_key:
            return {
                "success": False,
                "error": "ElevenLabs API key not configured"
            }
        
        if not text:
            return {
                "success": False,
                "error": "No text provided for synthesis"
            }
        
        try:
            # Clean text for TTS (remove PII if not consented)
            cleaned_text = self._clean_text_for_tts(text, params.get("allow_pii", False))
            
            response = await self.client.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "text": cleaned_text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.5
                    }
                }
            )
            
            if response.status_code == 200:
                # In production, save audio file and return URL
                audio_filename = f"audio_{hash(text)}.mp3"
                audio_path = f"/tmp/{audio_filename}"
                
                with open(audio_path, "wb") as f:
                    f.write(response.content)
                
                return {
                    "success": True,
                    "audio_url": audio_path,
                    "audio_filename": audio_filename,
                    "text_length": len(cleaned_text)
                }
            else:
                return {
                    "success": False,
                    "error": f"TTS API error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _list_voices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available voices"""
        if not self.api_key:
            return {
                "success": False,
                "error": "ElevenLabs API key not configured"
            }
        
        try:
            response = await self.client.get(
                f"{self.base_url}/voices",
                headers={"xi-api-key": self.api_key}
            )
            
            if response.status_code == 200:
                voices_data = response.json()
                return {
                    "success": True,
                    "voices": voices_data.get("voices", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _clean_text_for_tts(self, text: str, allow_pii: bool = False) -> str:
        """Clean text for TTS, removing PII if not allowed"""
        if allow_pii:
            return text
        
        import re
        
        # Remove phone numbers
        text = re.sub(r'\b(?:\+91|0)?[6-9]\d{9}\b', '[PHONE NUMBER]', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL ADDRESS]', text)
        
        # Remove potential names (basic pattern)
        text = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]', text)
        
        # Remove addresses (basic pattern)
        text = re.sub(r'\b\d+[^,\n]*(?:street|road|avenue|nagar|colony)[^,\n]*\b', '[ADDRESS]', text, flags=re.IGNORECASE)
        
        return text