import pytest
from backend.app.agents.graph import multi_agent_app
from backend.app.agents.state import AgentState

@pytest.mark.asyncio
async def test_multi_agent_chat_flow():
    initial_state: AgentState = {
        "user_id": "test_user_id",
        "conversation_id": "test_conv_id",
        "user_message": "Hello, what capabilities do you have for document generation?",
        "attached_doc_ids": [],
        "intent": "chat",
        "target_format": "none",
        "requires_research": False,
        "requires_rag": False,
        "document_structures": [],
        "rag_context": [],
        "research_results": [],
        "draft_content": {},
        "editing_instructions": {},
        "validation_result": {},
        "generated_doc_info": None,
        "final_response": "",
        "citations": [],
        "execution_logs": [],
        "errors": []
    }

    final_state = await multi_agent_app.ainvoke(initial_state)
    assert len(final_state["final_response"]) > 0
    assert len(final_state["execution_logs"]) > 0
    # Supervisor should have run
    agent_names = [log["agent"] for log in final_state["execution_logs"]]
    assert "Supervisor Agent" in agent_names
    assert "Response Agent" in agent_names

@pytest.mark.asyncio
async def test_multi_agent_generation_flow():
    initial_state: AgentState = {
        "user_id": "test_user_id",
        "conversation_id": "test_conv_id",
        "user_message": "Generate a new Word report for quarterly review",
        "attached_doc_ids": [],
        "intent": "document_generation",
        "target_format": "docx",
        "requires_research": False,
        "requires_rag": False,
        "document_structures": [],
        "rag_context": [],
        "research_results": [],
        "draft_content": {},
        "editing_instructions": {},
        "validation_result": {},
        "generated_doc_info": None,
        "final_response": "",
        "citations": [],
        "execution_logs": [],
        "errors": []
    }

    final_state = await multi_agent_app.ainvoke(initial_state)
    assert final_state["generated_doc_info"] is not None
    assert final_state["generated_doc_info"]["file_type"] == "docx"
