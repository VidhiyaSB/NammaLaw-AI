from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum

class TaskType(Enum):
    PARSE = "parse"
    RAG_SEARCH = "rag_search"
    WEB_SEARCH = "web_search"
    LLM_REASONING = "llm_reasoning"
    LLM_GENERATION = "llm_generation"
    TTS = "tts"
    CONNECTOR = "connector"
    SAFETY_CHECK = "safety_check"

class Task(BaseModel):
    id: str
    type: TaskType
    input_data: Dict[str, Any]
    dependencies: List[str] = []
    conditional: bool = False
    retry_count: int = 3

class TaskGraph(BaseModel):
    tasks: List[Task]
    
    def get_execution_order(self) -> List[Task]:
        """Return tasks in dependency-resolved order"""
        executed = set()
        ordered_tasks = []
        
        def can_execute(task: Task) -> bool:
            return all(dep in executed for dep in task.dependencies)
        
        remaining_tasks = self.tasks.copy()
        
        while remaining_tasks:
            ready_tasks = [task for task in remaining_tasks if can_execute(task)]
            
            if not ready_tasks:
                raise ValueError("Circular dependency detected in task graph")
            
            for task in ready_tasks:
                ordered_tasks.append(task)
                executed.add(task.id)
                remaining_tasks.remove(task)
        
        return ordered_tasks

class Citation(BaseModel):
    doc_id: str
    title: str
    source_type: str  # "statute", "case_law", "web"
    jurisdiction: str  # "tamil_nadu", "india", "web"
    confidence: float
    excerpt: str

class LegalOption(BaseModel):
    title: str
    description: str
    steps: List[str]
    estimated_cost: Optional[str] = None
    timeline: Optional[str] = None
    success_probability: Optional[str] = None

class ExecutionResult(BaseModel):
    success: bool
    summary: Optional[str] = None
    legal_options: List[LegalOption] = []
    draft_document: Optional[str] = None
    citations: List[Citation] = []
    audio_url: Optional[str] = None
    error: Optional[str] = None
    traces: List[Dict[str, Any]] = []
    confidence_score: Optional[float] = None