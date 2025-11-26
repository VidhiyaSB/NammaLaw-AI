import pytest
import asyncio
from src.orchestrator.main import TamilGuardianOrchestrator
from src.orchestrator.models import ExecutionResult

@pytest.mark.asyncio
async def test_orchestrator_basic_query():
    """Test basic query processing"""
    orchestrator = TamilGuardianOrchestrator()
    
    result = await orchestrator.process_legal_query(
        query="What are tenant rights in Tamil Nadu?",
        documents=None,
        user_preferences={"enable_audio": False}
    )
    
    assert isinstance(result, ExecutionResult)
    assert result.success is not None

@pytest.mark.asyncio
async def test_orchestrator_health_check():
    """Test health check functionality"""
    orchestrator = TamilGuardianOrchestrator()
    
    health = await orchestrator.health_check()
    
    assert isinstance(health, dict)
    assert "rag" in health
    assert "llm" in health

def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    orchestrator = TamilGuardianOrchestrator()
    
    assert orchestrator.planner is not None
    assert orchestrator.executor is not None
    assert orchestrator.mcp_manager is not None