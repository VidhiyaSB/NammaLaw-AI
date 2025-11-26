from typing import Dict, Any, List, Optional
from .models import TaskGraph, Task, TaskType
import logging

logger = logging.getLogger(__name__)

class TaskPlanner:
    """Plans execution tasks based on user input and requirements"""
    
    async def create_task_graph(
        self,
        query: str,
        documents: Optional[List[bytes]] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> TaskGraph:
        """
        Create a task execution graph based on the user query
        
        Args:
            query: User's legal question
            documents: Optional uploaded documents
            preferences: User preferences
            
        Returns:
            TaskGraph with ordered execution steps
        """
        tasks = []
        
        # Step 1: Parse documents if provided
        if documents:
            tasks.append(Task(
                id="parse_documents",
                type=TaskType.PARSE,
                input_data={"documents": documents},
                dependencies=[]
            ))
        
        # Step 2: RAG retrieval
        tasks.append(Task(
            id="rag_retrieval",
            type=TaskType.RAG_SEARCH,
            input_data={"query": query},
            dependencies=["parse_documents"] if documents else []
        ))
        
        # Step 3: Web search fallback (conditional)
        tasks.append(Task(
            id="web_search",
            type=TaskType.WEB_SEARCH,
            input_data={"query": query},
            dependencies=["rag_retrieval"],
            conditional=True
        ))
        
        # Step 4: LLM reasoning and summary
        tasks.append(Task(
            id="llm_reasoning",
            type=TaskType.LLM_REASONING,
            input_data={"query": query},
            dependencies=["rag_retrieval", "web_search"]
        ))
        
        # Step 5: Generate legal options
        tasks.append(Task(
            id="generate_options",
            type=TaskType.LLM_GENERATION,
            input_data={"type": "options"},
            dependencies=["llm_reasoning"]
        ))
        
        # Step 6: Draft legal documents
        tasks.append(Task(
            id="draft_documents",
            type=TaskType.LLM_GENERATION,
            input_data={"type": "draft"},
            dependencies=["generate_options"]
        ))
        
        # Step 7: TTS narration (optional)
        if preferences and preferences.get("enable_audio", False):
            tasks.append(Task(
                id="tts_narration",
                type=TaskType.TTS,
                input_data={},
                dependencies=["draft_documents"]
            ))
        
        return TaskGraph(tasks=tasks)