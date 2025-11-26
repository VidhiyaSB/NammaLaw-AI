import asyncio
from typing import Dict, Any, List, Optional
from .planner import TaskPlanner
from .executor import TaskExecutor
from .models import TaskGraph, ExecutionResult
from ..mcp_servers.base import MCPServerManager
import logging

logger = logging.getLogger(__name__)

class NammaLawOrchestrator:
    """Central orchestrator for NammaLaw AI Legal Assistant"""
    
    def __init__(self):
        self.planner = TaskPlanner()
        self.executor = TaskExecutor()
        self.mcp_manager = MCPServerManager()
        
    async def process_legal_query(
        self, 
        query: str, 
        documents: Optional[List[bytes]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Main entry point for processing legal queries
        
        Args:
            query: User's legal question or issue description
            documents: Optional uploaded documents
            user_preferences: User settings and preferences
            
        Returns:
            ExecutionResult with summary, options, drafts, and citations
        """
        try:
            # Step 1: Create task graph
            task_graph = await self.planner.create_task_graph(
                query=query,
                documents=documents,
                preferences=user_preferences
            )
            
            # Step 2: Execute task graph
            result = await self.executor.execute_graph(
                task_graph=task_graph,
                mcp_manager=self.mcp_manager
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing legal query: {e}")
            return ExecutionResult(
                success=False,
                error=str(e),
                summary="An error occurred while processing your request."
            )
    
    async def health_check(self) -> Dict[str, str]:
        """Check health of all MCP servers"""
        return await self.mcp_manager.health_check_all()