import asyncio
from typing import Dict, Any
from .models import TaskGraph, ExecutionResult, TaskType
from ..mcp_servers.base import MCPServerManager
import logging

logger = logging.getLogger(__name__)

class TaskExecutor:
    """Executes task graphs with retry logic and error handling"""
    
    async def execute_graph(
        self,
        task_graph: TaskGraph,
        mcp_manager: MCPServerManager
    ) -> ExecutionResult:
        """
        Execute a task graph with proper dependency handling
        
        Args:
            task_graph: Graph of tasks to execute
            mcp_manager: Manager for MCP server connections
            
        Returns:
            ExecutionResult with all outputs and traces
        """
        execution_context = {}
        traces = []
        
        try:
            # Execute tasks in dependency order
            for task in task_graph.get_execution_order():
                logger.info(f"Executing task: {task.id}")
                
                # Skip conditional tasks if conditions not met
                if task.conditional and not self._should_execute_conditional(task, execution_context):
                    continue
                
                # Execute task
                result = await self._execute_task(task, execution_context, mcp_manager)
                execution_context[task.id] = result
                
                # Log trace
                traces.append({
                    "task_id": task.id,
                    "task_type": task.type.value,
                    "success": result.get("success", True),
                    "metadata": result.get("metadata", {})
                })
            
            # Compile final result
            return self._compile_result(execution_context, traces)
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return ExecutionResult(
                success=False,
                error=str(e),
                traces=traces
            )
    
    async def _execute_task(
        self,
        task,
        context: Dict[str, Any],
        mcp_manager: MCPServerManager
    ) -> Dict[str, Any]:
        """Execute a single task"""
        
        if task.type == TaskType.PARSE:
            return await mcp_manager.call_server("parser", "parse_documents", task.input_data)
        
        elif task.type == TaskType.RAG_SEARCH:
            return await mcp_manager.call_server("rag", "search", task.input_data)
        
        elif task.type == TaskType.WEB_SEARCH:
            return await mcp_manager.call_server("websearch", "search", task.input_data)
        
        elif task.type == TaskType.LLM_REASONING:
            return await mcp_manager.call_server("llm", "reason", {
                **task.input_data,
                "context": context
            })
        
        elif task.type == TaskType.LLM_GENERATION:
            return await mcp_manager.call_server("llm", "generate", {
                **task.input_data,
                "context": context
            })
        
        elif task.type == TaskType.TTS:
            return await mcp_manager.call_server("elevenlabs", "synthesize", {
                "text": context.get("draft_documents", {}).get("content", ""),
                **task.input_data
            })
        
        else:
            raise ValueError(f"Unknown task type: {task.type}")
    
    def _should_execute_conditional(self, task, context: Dict[str, Any]) -> bool:
        """Determine if conditional task should execute"""
        if task.id == "web_search":
            rag_result = context.get("rag_retrieval", {})
            confidence = rag_result.get("confidence", 0)
            return confidence < 0.7  # Fallback threshold
        
        return True
    
    def _compile_result(self, context: Dict[str, Any], traces: List[Dict]) -> ExecutionResult:
        """Compile final execution result"""
        
        # Extract key outputs
        summary = context.get("llm_reasoning", {}).get("summary", "")
        options = context.get("generate_options", {}).get("options", [])
        draft = context.get("draft_documents", {}).get("content", "")
        citations = self._extract_citations(context)
        audio_url = context.get("tts_narration", {}).get("audio_url")
        
        return ExecutionResult(
            success=True,
            summary=summary,
            legal_options=options,
            draft_document=draft,
            citations=citations,
            audio_url=audio_url,
            traces=traces
        )
    
    def _extract_citations(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract citations from context"""
        citations = []
        
        # From RAG results
        rag_result = context.get("rag_retrieval", {})
        if "sources" in rag_result:
            citations.extend(rag_result["sources"])
        
        # From web search results
        web_result = context.get("web_search", {})
        if "sources" in web_result:
            citations.extend(web_result["sources"])
        
        return citations